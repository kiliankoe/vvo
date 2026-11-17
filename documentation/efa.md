# EFA JSON API Documentation

Base URL: `https://efa.vvo-online.de/std3`

## Overview

EFA (Elektronische Fahrplanauskunft) is the journey planner software from [MENTZ GmbH](https://www.mentz.net/) that VVO runs. Next to [TRIAS](trias.md) and [OJP](ojp.md), the same server answers EFA's own HTTP interface, which returns JSON when asked for it. VVO does not document this interface, but MENTZ does, and many other German transport associations serve it too.

**Key Characteristics:**

- GET requests with query parameters, JSON responses with `outputFormat=rapidJSON`
- No authentication required
- Stop search, departures and journey planning, with real-time data
- Usable from browsers for plain GET requests: responses carry `Access-Control-Allow-Origin: *`. Preflight (`OPTIONS`) requests are answered with HTTP 501
- Request times are local time (Europe/Berlin), response times are UTC

## Official Documentation

MobiData BW publishes two documents by MENTZ:

- **[EFA JSON-Schnittstelle, HTTP-Parameter Dokumentation](https://mobidata-bw.de/data/Dokumentation-EFA_JSON_Schnittstelle_V2.pdf)**: the parameter reference (German, 2021)
- **[EFA JSON API](https://mobidata-bw.de/daten/portal/efa-json/EFA_JSON_API_Training_EN_2.9.pdf)**: training slides with examples (English)

How a server behaves also depends on its configuration, so not everything in them applies to VVO.

## Common Parameters

| Parameter | Value | Description |
| --- | --- | --- |
| `outputFormat` | `rapidJSON` | JSON output. The default is an HTML page |
| `coordOutputFormat` | `WGS84[dd.ddddd]` | Coordinates in degrees, as latitude then longitude. The default is a projected coordinate system |

Parameters that describe a place end in a suffix that names its role: `_sf` in a stop search, `_dm` in a departure request, `_origin` and `_destination` in a trip request.

## Main Requests

### 1. XML_STOPFINDER_REQUEST

Find stops, addresses, or points of interest.

```bash
curl "https://efa.vvo-online.de/std3/XML_STOPFINDER_REQUEST?outputFormat=rapidJSON&coordOutputFormat=WGS84%5Bdd.ddddd%5D&type_sf=any&name_sf=Dresden%20Postplatz&anyObjFilter_sf=2"
```

| Parameter | Description |
| --- | --- |
| `type_sf` | `any` for a text search |
| `name_sf` | The search text |
| `anyObjFilter_sf` | Kinds of place to search for, as a sum of the values below. Without it, every kind is searched |
| `anyMaxSizeHitList` | Largest number of matches. Unreliable, see below |

Values for `anyObjFilter_sf`:

| Value | Kind |
| --- | --- |
| 1 | Localities |
| 2 | Stops |
| 4 | Streets |
| 8 | Addresses |
| 16 | Crossings |
| 32 | Points of interest |
| 64 | Postcodes |

For example, `34` (2 + 32) searches stops and points of interest. MENTZ notes that postcodes and crossings are rare in the data of German networks.

The matches are in `locations`, each with `id`, `name`, `type` (`stop`, `poi`, `street`, `singlehouse`, `suburb`, ...), `coord` and `matchQuality`. The list is not sorted, so sort by `matchQuality` to get the best match first. A stop's `name` includes the locality ("Dresden, Hauptbahnhof"), which is also in `parent`.

An ambiguous search is reported as an error in `systemMessages` (code `-8011`) and still returns its matches. A search without matches has the code `-8014`.

**Do not use `anyMaxSizeHitList` to limit a vague search.** The parameter cuts the list by match quality. MENTZ's documentation says that whether this happens before or after the server rates the matches depends on its configuration, and that the value "should not be too low" in the first case. On VVO, a low value makes vague searches come back empty:

| Search | `anyMaxSizeHitList` | Matches |
| --- | --- | --- |
| `Neustadt` | not set | 285 |
| `Neustadt` | 5, 10, 20 or 30 | 0 |
| `Neustadt` | 300 | 285 |
| `Zwinger` with `anyObjFilter_sf=32` | not set | 46 |
| `Zwinger` with `anyObjFilter_sf=32` | 40 | 40 |
| `Zwinger` with `anyObjFilter_sf=32` | 5 | 0 |
| `Dresden Neustadt` | 5 | 4 |

Leave the parameter out and cut the list yourself after sorting.

### 2. XML_DM_REQUEST

Get the departures of a stop.

```bash
curl "https://efa.vvo-online.de/std3/XML_DM_REQUEST?outputFormat=rapidJSON&coordOutputFormat=WGS84%5Bdd.ddddd%5D&type_dm=any&name_dm=de:14612:28&mode=direct&useRealtime=1&limit=10"
```

| Parameter | Description |
| --- | --- |
| `type_dm`, `name_dm` | The stop, as `any` and its ID |
| `mode` | `direct` returns departures right away. Without it the server first asks to confirm the stop |
| `useRealtime` | `1` for real-time data |
| `limit` | Largest number of departures |
| `itdDate`, `itdTime` | Start of the board as `YYYYMMDD` and `HHMM` in local time. Without them the board starts now |
| `itdDateTimeDepArr` | `dep` for departures |

The departures are in `stopEvents`, each with `departureTimePlanned`, `departureTimeEstimated` where real-time data exists, the `transportation` (line and destination) and the `location` (platform).

If `name_dm` does not name exactly one stop, the response has no `stopEvents` and lists the places the server considered in `locations`. There is no other sign of an unknown stop.

### 3. XML_TRIP_REQUEST2

Plan journeys between two places.

```bash
curl "https://efa.vvo-online.de/std3/XML_TRIP_REQUEST2?outputFormat=rapidJSON&coordOutputFormat=WGS84%5Bdd.ddddd%5D&type_origin=any&name_origin=de:14612:28&type_destination=any&name_destination=de:14612:13&useRealtime=1&calcNumberOfTrips=3"
```

| Parameter | Description |
| --- | --- |
| `type_origin`, `name_origin` | The start: `any` with an ID, or `coord` with `<longitude>:<latitude>:WGS84[dd.ddddd]` |
| `type_destination`, `name_destination` | The destination, in the same form |
| `calcNumberOfTrips` | Number of journeys |
| `itdDate`, `itdTime` | Date and time as `YYYYMMDD` and `HHMM` in local time |
| `itdTripDateTimeDepArr` | `dep` if the time is the departure, `arr` if it is the arrival |

The journeys are in `journeys`, each a list of `legs` with `origin`, `destination`, `transportation` and `stopSequence` (every call of the ride, including both ends).

Things to know when reading a journey:

- A change of platform inside a station is not a leg of its own. The ride before it carries a `footPathInfo` entry with the position `AFTER` and a duration in seconds.
- Estimated times at the ends of a leg are only real predictions if the leg has `isRealtimeControlled`. Without it they repeat the planned times or carry on the delay of the leg before.
- Walks are legs whose `transportation.product.class` is 99 or 100.
- VVO puts every train into product class 0. Trains without a line number are the long-distance ones.
- A request without journeys explains itself in `systemMessages`, for example with a place it could not resolve.

## Stop ID Format

The interface uses the same DHID format as [TRIAS](trias.md#stop-id-format): `de:14612:28` for a stop and `de:14612:28:2:4` for one of its platforms.
