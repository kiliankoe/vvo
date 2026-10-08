# VVO GTFS Data Documentation

## Overview

VVO/DVB transit data is available through Germany's national GTFS (General Transit Feed Specification) implementation. There is no standalone VVO GTFS feed — VVO data is part of the Germany-wide DELFI dataset, published through [GTFS.de](https://gtfs.de/).

## Data Sources

### Static GTFS Feed (DELFI)

**Download**: [gtfs.de/de/feeds/](https://gtfs.de/de/feeds/)

VVO data is included in the Germany-wide GTFS feeds. Available feed variants:

| Feed                         | Description                                  |
| ---------------------------- | -------------------------------------------- |
| Long-distance rail (`de_fv`) | ICE, IC, EC, EN                              |
| Regional rail (`de_rv`)      | RB, RE, IRE, S-Bahn                          |
| Local transit (`de_nv`)      | Trams, buses, ferries — **includes VVO/DVB** |
| Full (`de_full`)             | All of the above combined                    |

- gtfs.de states that feeds are generated daily, but the `Last-Modified` date of the download can lag several days behind
- Free versions cover about 30 days from the feed date
- Extended versions (paid) cover the full timetable period
- Over 20,000 transit lines, 500,000+ stops, ~2 million trips across Germany

The free local transit feed (`https://download.gtfs.de/germany/nv_free/latest.zip`, ~285 MB) contains:

- `agency.txt`: Transit agencies. DVB lines and most regional VVO buses are listed under "Verkehrsverbund Oberelbe", so DVB cannot be told apart. Some agencies are named just `-`.
- `stops.txt`: All stops with coordinates
- `routes.txt`: Transit lines
- `trips.txt`: Individual trips
- `stop_times.txt`: Scheduled arrival/departure times (~2.2 GB unpacked)
- `calendar.txt` / `calendar_dates.txt`: Service schedules and exceptions
- `feed_info.txt` / `attributions.txt`: Publisher and attribution

It has no shapes or fares. Stop, route, trip and service IDs are gtfs.de internal numbers, not DHIDs like `de:14612:28`, and they may change between feed versions. Regional rail such as the S-Bahn is in the separate `rv` feed. Rail line names like `S1` or `RB30` only show up here for replacement buses.

### VVO Snapshot

This repository publishes a VVO-area subset of the free local transit feed every week. A [workflow](../.github/workflows/update-gtfs.yml) runs [`scripts/fetch_gtfs.py`](../scripts/fetch_gtfs.py), which keeps every trip that touches a stop inside the bounding box of the stations in [`stations.json`](../data/stations.json). Trips are kept in full, including their stops outside the box, along with all routes, agencies, calendars and stops they reference. The result is about 6 MB zipped.

**Download**: [`https://github.com/kiliankoe/vvo/releases/latest/download/vvo-gtfs.zip`](https://github.com/kiliankoe/vvo/releases/latest/download/vvo-gtfs.zip)

Each snapshot is a release tagged `gtfs-YYYY-MM-DD` with the date it was built. The release notes list the service dates it covers. The last 8 releases are kept. The URL above always points to the newest one.

The workflow also commits a summary to [`data/gtfs/lines.csv`](../data/gtfs/lines.csv), so changes in service show up as diffs in the git history. It has one row per line:

| Column                              | Meaning                                                                                                |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `agency`, `line`, `type`            | `agency_name`, `route_short_name` and route type (e.g. `Tram`, `Bus`). Together they identify the line. |
| `mon` … `sun`                       | Typical number of trips on that weekday, counting both directions                                      |
| `first_departure`, `last_departure` | Earliest and latest departure of a regular trip from its first stop on any day                         |
| `stops`                             | Number of stations served by regular trips, counting all platforms of a station once                   |

The feed window is the range of service dates in the snapshot, about 30 days. The typical number of trips is the median over all dates of that weekday in the window, rounded up on ties. A single public holiday does not change it. School holidays that cover most of the window do, because many regional buses run less then. Lines with no typical trips on any weekday are left out. A regular trip runs on more than half of the dates of at least one weekday. Lines without one fall back to all their trips.

Times past midnight follow GTFS and continue counting, e.g. `25:30:00` is 1:30 on the next day. This also applies to the snapshot itself, so a list of departures for a date has to include late trips of the previous service day.

### GTFS Realtime

**URL**: `https://realtime.gtfs.de/realtime-free.pb`

- Updated every 10 seconds
- Contains **TripUpdates and Alerts only** — no VehiclePosition entities
- Format: Protocol Buffers (protobuf)
- Currently in beta
- Licensed under CC BY-SA 4.0

**Limitations:**

- The weekly [VVO snapshot](#vvo-snapshot) is usually too old to join against, since its IDs come from an earlier feed version. Use the current full feed instead.
- `route_id` is **not populated** in TripUpdates — only `trip_id` and `start_date` are set. Mapping trips to routes requires joining against the static GTFS `trips.txt`.
- Stop IDs are **GTFS.de internal numeric IDs** (e.g., `"188133"`), not DHID format (`de:14612:28`). Mapping requires the static `stops.txt`.
- Whether VVO data is included is difficult to confirm without the static data mappings, since the stop IDs don't match VVO's known formats.
- There are **no VehiclePosition entities**, so vehicle locations, `current_status`, and GPS coordinates are unavailable through this feed.

> **Note**: The domain `gtfs-rt.vvo.de` is not operational. As of February 2026, it resolves to a Plesk hosting panel with a mismatched SSL certificate and returns 404 on all feed paths. Use the `realtime.gtfs.de` feed above for TripUpdates, or the [WebAPI departure monitor](webapi.md#departure-monitor) for real-time stop-level data.

> **Alternative**: A GTFS-RT conversion of the DELFI [SIRI ET feed](siri.md) is available at `https://stc.traines.eu/mirror/german-delfi-siri/gtfsrt/`. This covers all VVO operators and is updated every ~2 minutes. See the [SIRI ET documentation](siri.md) for details on the source data.

## Working with GTFS Data

### Using Python

```python
import gtfs_kit as gk

# Load the VVO snapshot
feed = gk.read_feed('vvo-gtfs.zip', dist_units='km')

# Find Hauptbahnhof by name, since stop IDs are gtfs.de internal numbers.
# Platforms share the station's name, so this matches them too.
hbf = feed.stops[feed.stops['stop_name'] == 'Dresden Hauptbahnhof']

# Get all stop times there on one service day
day = feed.get_stop_times('20261012')
stop_times = day[day['stop_id'].isin(hbf['stop_id'])]
```

### Stop ID Mapping

gtfs.de stop IDs are internal numbers (e.g. `188133`). They match neither DHIDs (e.g. `de:14612:28`) nor WebAPI stop IDs (e.g. `33000028`). Mapping to VVO stops has to go by name or coordinates. The [VVO_STOPS.JSON](https://www.vvo-online.de/open_data/VVO_STOPS.JSON) file contains DHIDs and WebAPI IDs (`gid` and `id` fields) along with coordinates.

## Legal Framework

### License Terms

The data originates from [DELFI e.V.](https://www.delfi.de/) via [opendata-oepnv.de](https://www.opendata-oepnv.de/) and is redistributed by [gtfs.de](https://gtfs.de/). Please see there for licensing details.

gtfs.de states a Creative Commons 4.0 license for its static feeds but does not name the variant, so we could not confirm whether it is CC BY or CC BY-SA. The realtime feed is CC BY-SA 4.0, so assume share-alike to be safe. The source `attributions.txt` also credits OpenStreetMap contributors, which suggests parts of the data come from OpenStreetMap. The VVO snapshot keeps `attributions.txt` and `feed_info.txt` from the source feed. Credit DELFI e.V., gtfs.de and OpenStreetMap contributors when you use it.

### EU Regulation 2017/1926

- Mandates open access to transport data
- Machine-readable formats required
- National Access Points (NAP) required
- DELFI serves as Germany's national aggregator

## Data Quality Notes

- Static data is updated daily according to gtfs.de; the VVO snapshot is updated weekly
- Realtime data updates every 10 seconds (beta)
- gtfs.de stop IDs (`188133`) differ from DHIDs (`de:14612:28`) and WebAPI IDs (`33000028`)
- Some rural services may have limited realtime coverage

## Tools and Resources

### GTFS Tools

- [MobilityData GTFS Validator](https://gtfs-validator.mobilitydata.org/) — Official GTFS validator
- [GTFS-to-GeoJSON](https://github.com/BlinkTagInc/gtfs-to-geojson)
- [OpenTripPlanner](https://www.opentripplanner.org/) — Open source journey planner

### Data Portals

- [GTFS.de](https://gtfs.de/) — German GTFS aggregator (DELFI)
- [opendata-oepnv.de](https://www.opendata-oepnv.de/) — DELFI source data portal

### Documentation

- [GTFS Reference](https://gtfs.org/documentation/schedule/reference/)
- [GTFS Realtime Reference](https://gtfs.org/documentation/realtime/reference/)
- [DELFI](https://www.delfi.de/) — German national transit data platform

## Comparison with APIs

| Feature        | GTFS                   | APIs (Widget/WebAPI/TRIAS) |
| -------------- | ---------------------- | -------------------------- |
| Data freshness | Daily + realtime       | Real-time                  |
| Coverage       | Entire network         | Query-specific             |
| Format         | CSV / Protocol Buffers | JSON / XML                 |
| Use case       | Bulk data / analysis   | Interactive queries        |
| Authentication | None                   | None / API key             |
| Rate limits    | None (download)        | Yes                        |
