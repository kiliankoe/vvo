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

- Updated daily
- Free versions cover the next 7 days
- Extended versions (paid) cover the full timetable period
- Over 20,000 transit lines, 500,000+ stops, ~2 million trips across Germany

**GTFS contents:**

- `agency.txt` — Transit agencies (DVB, VMS, OVPS, etc.)
- `stops.txt` — All stops with coordinates
- `routes.txt` — Transit lines
- `trips.txt` — Individual trips
- `stop_times.txt` — Scheduled arrival/departure times
- `calendar.txt` / `calendar_dates.txt` — Service schedules and exceptions
- `shapes.txt` — Route geometries
- `fare_attributes.txt` / `fare_rules.txt` — Fare information

### GTFS Realtime

**URL**: `https://realtime.gtfs.de/realtime-free.pb`

- Updated every 10 seconds
- Contains **TripUpdates and Alerts only** — no VehiclePosition entities
- Format: Protocol Buffers (protobuf)
- Currently in beta
- Licensed under CC BY-SA 4.0

**Limitations:**

- `route_id` is **not populated** in TripUpdates — only `trip_id` and `start_date` are set. Mapping trips to routes requires joining against the static GTFS `trips.txt`.
- Stop IDs are **GTFS.de internal numeric IDs** (e.g., `"188133"`), not DHID format (`de:14612:28`). Mapping requires the static `stops.txt`.
- Whether VVO data is included is difficult to confirm without the static data mappings, since the stop IDs don't match VVO's known formats.
- There are **no VehiclePosition entities**, so vehicle locations, `current_status`, and GPS coordinates are unavailable through this feed.

> **Note**: The domain `gtfs-rt.vvo.de` is not operational. As of February 2026, it resolves to a Plesk hosting panel with a mismatched SSL certificate and returns 404 on all feed paths. Use the `realtime.gtfs.de` feed above for TripUpdates, or the [WebAPI departure monitor](webapi.md#departure-monitor) for real-time stop-level data.

## Working with GTFS Data

### Using Python

```python
import gtfs_kit as gk

# Load the Germany local transit feed (includes VVO)
feed = gk.read_feed('de_nv.zip')

# Get all stops in Dresden
dresden_stops = feed.stops[feed.stops['stop_name'].str.contains('Dresden')]

# Get routes for Hauptbahnhof
stop_times = feed.stop_times[feed.stop_times['stop_id'] == 'de:14612:28']
```

### Stop ID Mapping

GTFS stop IDs (e.g. `de:14612:28`) differ from WebAPI stop IDs (e.g. `33000028`). The [VVO_STOPS.JSON](https://www.vvo-online.de/open_data/VVO_STOPS.JSON) file contains both formats (`gid` and `id` fields) and can be used for mapping between them.

## Legal Framework

### License Terms

The data originates from [DELFI e.V.](https://www.delfi.de/) via [opendata-oepnv.de](https://www.opendata-oepnv.de/) and is redistributed by [gtfs.de](https://gtfs.de/). Please see there for licensing details.

### EU Regulation 2017/1926

- Mandates open access to transport data
- Machine-readable formats required
- National Access Points (NAP) required
- DELFI serves as Germany's national aggregator

## Data Quality Notes

- Static data is updated daily
- Realtime data updates every 10 seconds (beta)
- Stop IDs differ between GTFS (`de:14612:28`) and WebAPI (`33000028`) formats
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
