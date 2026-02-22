# VVO SIRI ET Real-Time Data

## Overview

Real-time transit data for the VVO/Oberelbe region is available as a **SIRI ET (Estimated Timetable)** feed, provided by [DELFI e.V.](https://www.delfi.de/) via Germany's national data platform [Mobilithek](https://mobilithek.info/offers/832220950725300224). SIRI (Service Interface for Real-time Information) is a European standard (CEN/TS 15531) for exchanging real-time public transport information.

The Oberelbe feed covers the full VVO network — trams, buses, regional rail, S-Bahn, and ferries — including real-time delay predictions, cancellations, occupancy levels, and platform assignments.

## Data Access

### Official Source (Mobilithek)

The canonical source is DELFI's Mobilithek offering:

**Mobilithek page**: [mobilithek.info/offers/832220950725300224](https://mobilithek.info/offers/832220950725300224)

Access requires registration on Mobilithek and activation by DELFI e.V.

### Community Mirror (traines.eu)

A freely accessible mirror is maintained at [stc.traines.eu](https://stc.traines.eu/mirror/german-delfi-siri/oberelbe/):

| Resource           | URL                                                                                 |
| ------------------ | ----------------------------------------------------------------------------------- |
| Latest feed        | `https://stc.traines.eu/mirror/german-delfi-siri/oberelbe/latest-oberelbe.siri.xml` |
| Hourly snapshots   | `https://stc.traines.eu/mirror/german-delfi-siri/oberelbe/{date}T{hour}+01:00/`     |
| Long-term archive  | `https://mirror.traines.eu/german-delfi-siri/oberelbe/`                             |
| GTFS-RT conversion | `https://stc.traines.eu/mirror/german-delfi-siri/gtfsrt/`                           |

- The latest feed is updated approximately **every 5 minutes**
- Hourly snapshot directories contain individual timestamped XML files (~5 minute intervals)
- The long-term archive at `mirror.traines.eu` stores daily archives as `.tar.br` (Brotli-compressed tar) files going back to October 2025
- A GTFS-RT (protobuf) conversion of the combined Germany-wide SIRI data is also available

### Feed Size

A typical `latest-oberelbe.siri.xml` file is **~12–15 MB** of XML, containing around 1,200 vehicle journeys with ~20,000 estimated stop calls.

## Data Format

The feed uses **SIRI 2.0** XML with the `EstimatedTimetableDelivery` service. Each update contains a single `EstimatedJourneyVersionFrame` with all currently active vehicle journeys.

### XML Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Siri xmlns="http://www.siri.org.uk/siri" version="2.0">
  <ServiceDelivery>
    <ResponseTimestamp>2026-02-22T19:49:51.452Z</ResponseTimestamp>
    <ProducerRef>rcsued-siri-vvo</ProducerRef>
    <EstimatedTimetableDelivery version="2.0">
      <EstimatedJourneyVersionFrame>
        <RecordedAtTime>2026-02-22T19:49:51.452Z</RecordedAtTime>

        <EstimatedVehicleJourney>
          <!-- Journey-level fields -->
          <RecordedAtTime>2026-02-22T20:28:30Z</RecordedAtTime>
          <LineRef>de:vvo:23-160</LineRef>
          <DirectionRef>1</DirectionRef>
          <PublishedLineName>160</PublishedLineName>
          <DirectionName>Weißeritzpark</DirectionName>
          <OperatorRef>vvorbl#!ADD!#VVO_ADB_DELFI_Out</OperatorRef>
          <ProductCategoryRef>RVS160</ProductCategoryRef>
          <Monitored>true</Monitored>

          <!-- Stop-level predictions -->
          <EstimatedCalls>
            <EstimatedCall>
              <StopPointRef>de:14612:140:1:1</StopPointRef>
              <AimedDepartureTime>2026-02-22T20:57:00Z</AimedDepartureTime>
              <ExpectedDepartureTime>2026-02-22T20:57:00Z</ExpectedDepartureTime>
            </EstimatedCall>
            <!-- ... more stops ... -->
          </EstimatedCalls>
          <IsCompleteStopSequence>true</IsCompleteStopSequence>
        </EstimatedVehicleJourney>

        <!-- ... more journeys ... -->
      </EstimatedJourneyVersionFrame>
    </EstimatedTimetableDelivery>
  </ServiceDelivery>
</Siri>
```

### EstimatedVehicleJourney Fields

| Field                     | Description                                                           | Example                              |
| ------------------------- | --------------------------------------------------------------------- | ------------------------------------ |
| `RecordedAtTime`          | When this journey's data was last updated                             | `2026-02-22T20:28:30Z`               |
| `LineRef`                 | DELFI line identifier                                                 | `de:vvo:23-160`                      |
| `DirectionRef`            | Direction (typically `1` or `2`)                                      | `1`                                  |
| `PublishedLineName`       | Public-facing line number                                             | `160`, `4`, `S 1`, `RE1`             |
| `DirectionName`           | Destination/direction name                                            | `Weißeritzpark`, `Prohlis`           |
| `OperatorRef`             | Operator identifier (suffixed with `#!ADD!#VVO_ADB_DELFI_Out`)        | `DVB`, `vvorbl`, `CVAG`              |
| `ProductCategoryRef`      | Transport mode/product                                                | `Tram`, `Bus`, `RE`, `RVS160`        |
| `Monitored`               | Whether real-time tracking is active                                  | `true` / `false`                     |
| `PredictionInaccurate`    | Whether predictions may be unreliable                                 | `true` / `false`                     |
| `Cancellation`            | Whether the entire journey is cancelled                               | `true` (only present when cancelled) |
| `ExtraJourney`            | Whether this is an unscheduled extra service                          | `true` (only present for extras)     |
| `VehicleJourneyRef`       | Internal journey reference                                            |                                      |
| `FramedVehicleJourneyRef` | Contains `DataFrameRef` (date) and `DatedVehicleJourneyRef` (trip ID) |                                      |
| `IsCompleteStopSequence`  | Whether all stops of the trip are included                            | `true` / `false`                     |

### EstimatedCall Fields (Future Stops)

| Field                   | Description                                  | Example                                       |
| ----------------------- | -------------------------------------------- | --------------------------------------------- |
| `StopPointRef`          | DHID stop identifier                         | `de:14612:140:1:1`                            |
| `VisitNumber`           | Visit sequence number (typically `100`)      | `100`                                         |
| `AimedArrivalTime`      | Scheduled arrival (UTC)                      | `2026-02-22T20:58:00Z`                        |
| `ExpectedArrivalTime`   | Predicted arrival (UTC)                      | `2026-02-22T20:59:46Z`                        |
| `AimedDepartureTime`    | Scheduled departure (UTC)                    | `2026-02-22T20:58:00Z`                        |
| `ExpectedDepartureTime` | Predicted departure (UTC)                    | `2026-02-22T20:59:46Z`                        |
| `ArrivalPlatformName`   | Platform/track for arrival                   | `1`, `2`                                      |
| `DeparturePlatformName` | Platform/track for departure                 | `1`, `2`                                      |
| `DestinationDisplay`    | Headsign/destination shown on vehicle        | `Pl.d.Solidarität`                            |
| `Occupancy`             | Current occupancy level                      | `seatsAvailable`, `standingAvailable`, `full` |
| `Cancellation`          | Whether this specific stop is cancelled      | `true`                                        |
| `ExtraCall`             | Whether this is an unscheduled extra stop    | `true` / `false`                              |
| `PredictionInaccurate`  | Whether this stop's prediction is unreliable | `true` / `false`                              |

### RecordedCall Fields (Past Stops)

Journeys may also contain `<RecordedCalls>` for stops the vehicle has already passed. These have the same fields as `EstimatedCall` but represent observed (not predicted) data.

## Operators in the Feed

The Oberelbe feed covers 16 transit operators:

| Operator ID | Name                                  | Typical journeys |
| ----------- | ------------------------------------- | ---------------- |
| `DVB`       | Dresdner Verkehrsbetriebe (tram, bus) | ~400             |
| `vvorbl`    | VVO Regionalbus                       | ~180             |
| `CVAG`      | Chemnitzer Verkehrs-AG                | ~170             |
| `DDS-LB`    | DB (Länderbahn, Vogtlandbahn etc.)    | ~110             |
| `DDS-ODEG`  | Ostdeutsche Eisenbahn                 | ~110             |
| `SVZ`       | Städteverbindung Zwickau              | ~75              |
| `DDIP-PSB`  | DB (Personenverkehr Sachsen/Bayern)   | ~45              |
| `MRBO`      | Mitteldeutsche Regiobahn              | ~40              |
| `RBM`       | Regionalbus Mittelsachsen             | ~25              |
| `BOS`       | DB Bus Ost                            | ~25              |
| `RVE`       | Regionalverkehr Erzgebirge            | ~25              |
| `RVW`       | Regionalverkehr Westsachsen           | ~15              |
| `DRO`       | Dresdner Nahverkehr                   | ~3               |
| `ownRBL`    | Own dispatching system                | ~2               |
| `FEG`       | Freiberger Eisenbahngesellschaft      | ~1               |
| `DDIP-VMIV` | DB (VMIV region)                      | ~1               |

Journey counts are approximate and vary by time of day.

## Transport Modes

The `ProductCategoryRef` field indicates the transport mode. Values found in the feed include:

- **Tram/Straßenbahn**: `Tram`, `TRAM`, `Strab`, `STRABA`, `Straßenbahn`
- **Bus**: `Bus`, `BUS`, `Regionalbus`, `KOM`
- **S-Bahn**: `RVSS 1`, `RVSS 3`, `RVSH/S`
- **Regional rail**: `RE`, `RB`, various operator-specific codes (`MRBO#RE`, `FEG#RB`, `VBG`, etc.)
- **Long-distance/express**: `TLX`, `ALX`, `EX`, `TL`
- **Replacement services**: `SEV` (Schienenersatzverkehr)
- **Specific bus lines**: `RVS100`, `RVS160`, `VGM400`, `RBO11`, etc.

## Stop ID Format

Stop IDs use the German DHID (Deutschlandweite Haltestellenkennung) format:

```
de:{district}:{stop}:{area}:{platform}
```

Examples:

- `de:14612:140:1:1` — Stop in district 14612 (Freital), stop 140, area 1, platform 1
- `de:14627:4218:1:1` — Stop in district 14627 (Dresden), stop 4218
- `cz:55413:683` — Czech stop (cross-border services to Czech Republic)

The district codes correspond to German administrative district numbers (Kreisschlüssel). Dresden is `14612` (city) and `14627`.

## Delay Detection

Delays are detected by comparing aimed and expected times:

```python
from datetime import datetime

aimed = datetime.fromisoformat("2026-02-22T19:48:00+00:00")
expected = datetime.fromisoformat("2026-02-22T19:50:08+00:00")
delay_seconds = (expected - aimed).total_seconds()  # 128 seconds ≈ 2 min delay
```

When `AimedDepartureTime` equals `ExpectedDepartureTime`, the vehicle is on schedule. In a typical feed snapshot, roughly 15–20% of stop calls show a delay.

## Example: Parsing with Python

```python
import xml.etree.ElementTree as ET
from datetime import datetime

ns = {"s": "http://www.siri.org.uk/siri"}

tree = ET.parse("latest-oberelbe.siri.xml")
root = tree.getroot()

for journey in root.iter("{http://www.siri.org.uk/siri}EstimatedVehicleJourney"):
    line = journey.findtext("s:PublishedLineName", namespaces=ns)
    direction = journey.findtext("s:DirectionName", namespaces=ns)
    cancelled = journey.findtext("s:Cancellation", namespaces=ns) == "true"

    if cancelled:
        print(f"Line {line} -> {direction}: CANCELLED")
        continue

    for call in journey.iter("{http://www.siri.org.uk/siri}EstimatedCall"):
        stop = call.findtext("s:StopPointRef", namespaces=ns)
        aimed = call.findtext("s:AimedDepartureTime", namespaces=ns)
        expected = call.findtext("s:ExpectedDepartureTime", namespaces=ns)
        occupancy = call.findtext("s:Occupancy", namespaces=ns)
        platform = call.findtext("s:DeparturePlatformName", namespaces=ns)

        delay = ""
        if aimed and expected and aimed != expected:
            diff = datetime.fromisoformat(expected) - datetime.fromisoformat(aimed)
            delay = f" (+{int(diff.total_seconds())}s)"

        print(f"Line {line} -> {direction} | {stop} | {aimed}{delay}"
              + (f" | Platform {platform}" if platform else "")
              + (f" | {occupancy}" if occupancy else ""))
```

## Related Resources

- [SIRI Standard (Wikipedia)](https://en.wikipedia.org/wiki/Service_Interface_for_Real_Time_Information)
- [SIRI 2.0 Specification (CEN)](https://www.transmodel-cen.eu/siri-standard/)
- [DELFI e.V.](https://www.delfi.de/) — German national transit data coordination
- [Mobilithek](https://mobilithek.info/) — Germany's national mobility data platform
- [GTFS Data](gtfs.md) — Alternative real-time format (GTFS-RT conversion available)
- [WebAPI](webapi.md) — VVO's JSON API with per-stop real-time departures
- [TRIAS API](trias.md) — VVO's official XML API
