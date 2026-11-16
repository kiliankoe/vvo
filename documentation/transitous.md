# Transitous API Documentation

Base URL: `https://api.transitous.org/api/`

## Overview

[Transitous](https://transitous.org/) is a community-run public instance of the [MOTIS](https://github.com/motis-project/motis) journey planner. It covers Europe and other regions with open GTFS, GTFS-RT, SIRI and GBFS feeds. For the VVO area it uses DELFI's nationwide GTFS and real-time data, the origin of the feeds on the [GTFS](gtfs.md) and [SIRI ET](siri.md) pages. FlixBus, Czech rail and the MOBIbike Dresden bike sharing feed come from separate sources.

For DVB departures, prefer the [WebAPI](webapi.md). It is VVO's own system and carries route change notices, which Transitous lacks, see [Data Quality in Dresden](#data-quality-in-dresden). Transitous is the better choice for journeys that leave the VVO area or cross the border.

**Key Characteristics:**

- JSON responses to plain GET requests
- No authentication required
- Usable from browsers, because every response, including CORS preflight (`OPTIONS`) requests, carries `Access-Control-Allow-Origin: *`
- Open-source, non-commercial projects only, see [Usage Policy](#usage-policy)
- Stop search, departures, journey planning, trip details, stops on a map and bike sharing
- Journey planning uses real-time data, so it avoids connections that a delay has broken
- Timetables are imported daily. Real-time feeds are polled every 60 seconds
- The `server` response header names the MOTIS version, e.g. `MOTIS v2.11.4`

## Official Documentation

- **API reference**: The Transitous [API page](https://transitous.org/api/) links the OpenAPI spec of the MOTIS version it runs. Endpoint versions such as `v6` change with MOTIS releases
- **Data sources and licenses**: [transitous.org/sources](https://transitous.org/sources/)
- **Status**: [splinestatus.de/status/transitous](https://splinestatus.de/status/transitous)
- **Feed configuration**: [`feeds/de.json`](https://github.com/public-transport/transitous/blob/main/feeds/de.json) in the Transitous repository
- **Contact**: Matrix room [#transitous:matrix.spline.de](https://matrix.to/#/%23transitous:matrix.spline.de)

## Usage Policy

Transitous is run by volunteers on a best-effort basis. They may stop serving any client at any time. The [API page](https://transitous.org/api/) states these rules:

- Your project has to be open source and must not be commercial.
- Every request needs a `User-Agent` header with the application name, its version and a contact (email address or website), e.g. `my-app/1.0 (+https://example.org)`. Browser apps that cannot set it may rely on the `Referer` header, with contact details on their website.
- Link to [transitous.org/sources](https://transitous.org/sources/) in a visible place and follow the conditions of those sources, including the OpenStreetMap attribution guidelines.
- Ask in the Matrix room before you send more than 720 requests a day to `/plan`, `/one-to-many` or `/one-to-all`, or before you serve many users or run automated requests.
- There is no need to scrape the API. The [whole dataset](https://github.com/public-transport/transitous/wiki/Using-Transitous-data) can be downloaded from `https://api.transitous.org/source-data/processed/`.
- Applications must not use the staging instance `staging.api.transitous.org` or the internal hosts behind the API.

There are no rate limit headers. The limits above are the policy.

## Stop ID Format

Stop IDs start with the name of the feed they come from. For VVO stops that is `de-DELFI_`, followed by the [DHID](trias.md#stop-id-format):

| Example | Meaning |
| --- | --- |
| `de-DELFI_de:14612:28` | Dresden Hauptbahnhof (station) |
| `de-DELFI_de:14612:37:1:1` | Dresden Postplatz, platform 1 |

Most Dresden stations have no station-level entry. Only their platforms exist, without a parent. `de-DELFI_de:14612:28` works, but `de-DELFI_de:14612:37` (Postplatz) and `de-DELFI_de:14612:13` (Albertplatz) fail with HTTP 404 and `{"error":"no radius: stop_found=false, center_parsed=false"}`. Query departures with any platform ID or with coordinates instead, see [Departures](#2-departures). Stop search returns IDs that work.

Stops from other feeds have other prefixes. Dresden Hauptbahnhof also exists as `de-VBB_de:14612:28`, and FlixBus stops start with `eu-flixbus_`.

Trip IDs such as `20261116_10:43_de-DELFI_3453249978` change with every timetable import. Do not store them.

## Main Endpoints

### 1. Stop Search

GET `/api/v1/geocode`

| Parameter | Description |
| --- | --- |
| `text` | Search text, required |
| `type` | `STOP`, `ADDRESS` or `PLACE`, comma-separated. Default is all types |
| `language` | Language for names, e.g. `de` |

The response is an array of matches with `type`, `name`, `id`, `lat`, `lon`, `modes` and `areas`. Names can differ between endpoints: stop search returns `Dresden Hbf`, departures `Dresden Hauptbahnhof`. For many stations the `id` is a platform ID, e.g. `de-DELFI_de:14612:13:1:1` for Albertplatz.

### 2. Departures

GET `/api/v6/stoptimes`

| Parameter | Description |
| --- | --- |
| `stopId` | Stop ID. A platform ID returns the departures of all platforms of the station, because stops with a similar name count as equivalent |
| `center` | `latitude,longitude`, used when `stopId` is missing or unknown. Requires `radius` |
| `radius` | Radius in meters. Includes all stops within it |
| `exactRadius` | `true` returns only stops physically inside `radius`. With `radius=0` it returns just the given platform |
| `n` | Minimum number of departures. Either `n` or `window` is required |
| `window` | Time window in seconds, as an alternative to `n` |
| `time` | ISO 8601 start time, default now |
| `arriveBy` | `true` for arrivals |
| `mode` | Allowed modes, e.g. `TRAM,BUS` |
| `withAlerts` | `false` leaves out service alerts. Default is `true` |
| `pageCursor` | Cursor from `previousPageCursor` or `nextPageCursor` |

The response has `stopTimes`, `place` and the two page cursors. A shortened departure:

```json
{
  "place": {
    "name": "Dresden Hauptbahnhof",
    "stopId": "de-DELFI_de:14612:28:3:1",
    "departure": "2026-11-16T10:03:00Z",
    "scheduledDeparture": "2026-11-16T10:03:00Z",
    "scheduledTrack": "1",
    "track": "1",
    "departureTimestampReason": "PROPAGATED"
  },
  "mode": "TRAM",
  "realTime": true,
  "headsign": "Weixdorf",
  "agencyName": "DVB-Straßenbahn",
  "routeShortName": "7",
  "displayName": "7",
  "routeColor": "9e0234",
  "tripId": "20261116_10:43_de-DELFI_3453249978",
  "cancelled": false,
  "tripCancelled": false
}
```

Times are in UTC. `departureTimestampReason` tells where the time comes from:

| Value | Meaning |
| --- | --- |
| `NO_RT_DATA` | No real-time data, the time is the scheduled time |
| `PREDICTED` | Prediction from the real-time source for this stop |
| `PROPAGATED` | Delay carried over from an earlier stop of the trip |
| `OBSERVED` | Recorded actual time |
| `INCONSISTENT_RT` | Time corrected by MOTIS because the real-time data did not fit |

Headsigns come from the DELFI timetable and can differ from the WebAPI, e.g. `Altenberg Bahnhof` where the WebAPI shows `Altenberg - 398 Teplice`. Rail tracks mostly come as `Gl.13` or `Gl. 3`, sometimes as a plain number. Tram and bus platforms are plain numbers.

### 3. Journey Planning

GET `/api/v6/plan`

| Parameter | Description |
| --- | --- |
| `fromPlace`, `toPlace` | Stop ID or `latitude,longitude`, required |
| `time` | ISO 8601 time, default now |
| `arriveBy` | `true` if `time` is the arrival time |
| `maxTransfers` | Maximum number of transfers |
| `transitModes` | Allowed modes, e.g. `TRAM,BUS,SUBURBAN` |
| `detailedTransfers` | `false` leaves out the walking routes between platforms and makes the response smaller |

The response lists `itineraries`, each with `startTime`, `endTime`, `duration`, `transfers` and `legs`. A leg has the same line fields as a departure, plus `from`, `to` and an encoded `legGeometry`. By default routing uses real-time data. `realtimeMode=OFF` plans on the timetable only.

### 4. Further Endpoints

- `/api/v6/trip?tripId=…` returns one trip with all stops as an itinerary.
- `/api/v6/map/stops?min=lat,lon&max=lat,lon` returns the stops in a bounding box.
- `/api/v1/rentals?point=lat,lon&radius=…` returns bike sharing stations and vehicles, for Dresden MOBIbike with live availability and app links.

The OpenAPI spec lists their parameters and the remaining endpoints, such as reachability searches and reverse geocoding.

## Examples

Find a stop:

```bash
curl -A "my-app/1.0 (+https://example.org)" \
  "https://api.transitous.org/api/v1/geocode?text=Dresden%20Albertplatz&type=STOP"
```

Departures at Postplatz, by platform ID and by coordinates:

```bash
curl -A "my-app/1.0 (+https://example.org)" \
  "https://api.transitous.org/api/v6/stoptimes?stopId=de-DELFI_de:14612:37:1:1&n=10"

curl -A "my-app/1.0 (+https://example.org)" \
  "https://api.transitous.org/api/v6/stoptimes?center=51.050836,13.733516&radius=150&n=10"
```

Journey from Hauptbahnhof to Albertplatz:

```bash
curl -A "my-app/1.0 (+https://example.org)" \
  "https://api.transitous.org/api/v6/plan?fromPlace=de-DELFI_de:14612:28&toPlace=de-DELFI_de:14612:13:1:1&detailedTransfers=false"
```

## Data Quality in Dresden

As of 2026-11-16, from samples on a Monday morning (11:04 and 11:17 CET), compared with the [WebAPI departure monitor](webapi.md#departure-monitor) at the same time. Departures were paired by line, scheduled time and platform. "Same minute" means both predicted the same departure minute. The comparison shows where the sources differ, not which one was right.

| Stop | Time | Departures WebAPI / Transitous / paired | Real-time in both | Same minute | 1 min apart | 2+ min apart |
| --- | --- | --- | --- | --- | --- | --- |
| Hauptbahnhof | 11:04 | 57 / 62 / 55 | 50 | 36 | 8 | 6 |
| Hauptbahnhof | 11:17 | 55 / 61 / 54 | 51 | 44 | 6 | 1 |
| Postplatz | 11:04 | 60 / 60 / 58 | 58 | 40 | 13 | 5 |
| Postplatz | 11:17 | 60 / 58 / 58 | 58 | 42 | 11 | 5 |
| Albertplatz | 11:04 | 58 / 60 / 58 | 58 | 48 | 6 | 4 |
| Bannewitz Windbergstraße | 11:04 | 29 / 30 / 29 | 9 | 7 | 0 | 2 |

- Of the departures with real-time data in both sources, about three in four agreed to the minute and about nine in ten within one minute. Where they were 2 or more minutes apart, the WebAPI mostly showed the larger delay.
- DVB trams and buses had real-time data on every departure, always propagated from earlier stops (`PROPAGATED`). Regional buses had it for some trips only, 9 of 29 at Bannewitz.
- Some scheduled times differed from the WebAPI where it listed a route change. Bus 68 at Postplatz was scheduled 2 to 3 minutes earlier. The predicted times still agreed within a minute.
- No service alerts were returned for Dresden stops, while the WebAPI listed route changes.
- Transitous also lists FlixBus departures and rail replacement buses at Hauptbahnhof, which the WebAPI departure monitor did not show.

Journeys within Dresden used the same lines and times as the WebAPI [trip query](webapi.md#query-a-trip). When a feeder bus was 10 minutes late, Transitous planned the next possible tram, while the WebAPI still offered the missed one.

## License

Static DELFI timetables are licensed CC BY 4.0, DELFI real-time data CC BY-SA 4.0, and map and address data come from OpenStreetMap under the ODbL. Every response carries `Link: <https://transitous.org/sources/>; rel="license"`. Link that page in your application.

## Client Libraries

- [`@motis-project/motis-client`](https://www.npmjs.com/package/@motis-project/motis-client): JavaScript/TypeScript client generated from the OpenAPI spec
- [`@motis-project/motis-fptf-client`](https://www.npmjs.com/package/@motis-project/motis-fptf-client): MOTIS in the Friendly Public Transport Format
- [KPublicTransport](https://invent.kde.org/libraries/kpublictransport): C++/Qt library
- [Travel::Status::MOTIS](https://finalrewind.org/projects/Travel-Status-MOTIS/): Perl module
