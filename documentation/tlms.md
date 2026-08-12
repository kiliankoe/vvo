# TLMS Live Vehicle Positions

## Overview

[TLMS (Transit Live Mapping Solutions)](https://tlm.solutions) is a community project that tracks vehicles in real time by receiving the **R09 radio telegrams** trams and buses transmit for traffic light priority (VDV 420). Software-defined radio receivers around the city decode these telegrams and TLMS publishes the resulting vehicle positions through a public WebSocket and several HTTP APIs.

For Dresden this yields live positions of DVB vehicles, including line, run number and delay. The data is independent of VVO/DVB systems, but coverage depends on receiver placement and only vehicles that emit R09 telegrams show up. Positions are interpolated between reporting points.

A live map is available at [kid.tlm.solutions/de/map/0](https://kid.tlm.solutions/de/map/0?x=13.7456&y=51.0489&z=13&r=0&l=111) (the `0` is the region ID for Dresden).

⚠️ TLMS is a volunteer-run community project without availability guarantees. The full stack is open source at [github.com/tlm-solutions](https://github.com/tlm-solutions), documentation lives at [docs.tlm.solutions](https://docs.tlm.solutions).

## WebSocket Endpoint

```
wss://socket.tlm.solutions
```

Vehicle position updates start streaming as JSON messages immediately after connecting, one JSON object per message. No authentication is required.

### Quick Start

```bash
websocat wss://socket.tlm.solutions
```

```json
{
  "source": 1,
  "time": "1786535656711",
  "lat": 51.048192923076961,
  "lon": 13.743153307692344,
  "line": 62,
  "run": 4,
  "delayed": 120,
  "r09_reporting_point": 11266,
  "r09_destination_number": 232
}
```

### Message Format

Messages correspond to the TLMS [`Waypoint`](https://github.com/tlm-solutions/tlms.rs/blob/main/src/locations/waypoint.rs) struct:

| Field                    | Type    | Description                                                            |
| ------------------------ | ------- | ---------------------------------------------------------------------- |
| `id`                     | Integer | Unique waypoint identifier (not always present)                        |
| `source`                 | Integer | Data source: `0` unknown, `1` R09 telegram, `2` GPS via Trekkie        |
| `time`                   | String  | Unix timestamp in milliseconds (serialized as string)                  |
| `region`                 | Integer | Region ID (present when subscribed to multiple regions)                |
| `lat` / `lon`            | Float   | Vehicle position (interpolated between reporting points)               |
| `line`                   | Integer | Line number (e.g. `3`, `62`)                                           |
| `run`                    | Integer | Run number ("Kurs/Laufnummer") identifying the vehicle on its line     |
| `delayed`                | Float   | Delay in seconds, negative values mean the vehicle is early (optional) |
| `r09_reporting_point`    | Integer | ID of the reporting point the telegram was sent from (optional)        |
| `r09_destination_number` | Integer | Destination number from the R09 telegram (optional)                    |

### Filtering

Send a JSON filter object to the socket to narrow the stream. Sending another filter overwrites the previous one.

```json
{
  "lines": [9, 11],
  "positions": [],
  "regions": [0],
  "enrich": true
}
```

| Field       | Description                                                    |
| ----------- | -------------------------------------------------------------- |
| `lines`     | Only emit updates for these line numbers (empty = all)         |
| `positions` | Only emit updates for these reporting point IDs (empty = all)  |
| `regions`   | Only emit updates for these region IDs (e.g. `0` = Dresden)    |
| `enrich`    | Request enriched waypoints (currently returns the same fields) |

Example — only Dresden trams on line 3:

```bash
echo '{"regions": [0], "lines": [3]}' | websocat -n wss://socket.tlm.solutions
```

### Regions

Region metadata is available from the Datacare API:

```bash
curl https://datacare.tlm.solutions/v1/region
```

Dresden is region `0`. Other regions (Chemnitz, Hannover, …) exist with varying degrees of coverage.

## Related HTTP APIs

TLMS also runs Swagger-documented REST APIs:

| Service  | URL                                                                              | Purpose                                    |
| -------- | -------------------------------------------------------------------------------- | ------------------------------------------ |
| Datacare | [datacare.tlm.solutions/swagger-ui/](https://datacare.tlm.solutions/swagger-ui/) | Regions, stations and R09 telegram data    |
| Lizard   | [lizard.tlm.solutions/swagger-ui/](https://lizard.tlm.solutions/swagger-ui/)     | Current network state (live vehicle state) |
| Trekkie  | [trekkie.tlm.solutions/swagger-ui/](https://trekkie.tlm.solutions/swagger-ui/)   | GPS track submission and retrieval         |

## See Also

- [TLMS documentation](https://docs.tlm.solutions) — architecture and service overview
- [R09 telegram background](https://docs.tlm.solutions/background/public-transport-acceleration-technologies.md) — how the radio telegrams work
- [funnel](https://github.com/tlm-solutions/funnel) — the service behind the WebSocket endpoint
