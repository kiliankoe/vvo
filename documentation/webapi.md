# VVO WebAPI Documentation

Base URL: `https://webapi.vvo-online.de`

## Overview

The WebAPI is a JSON-based REST interface used by VVO's mobile web portal (vvo-mobil.de) and the official DVB mobil app. It provides comprehensive access to transit data including stop search, departure monitors, trip planning, route change information, map data, and tariff zone polygons.

**Key Characteristics:**

- Most endpoints use POST requests with JSON payloads (exception: PointFinder uses GET)
- All requests include `"format": "json"` in the payload or query string
- Responses use Microsoft JSON date format: `/Date(timestamp+timezone)/`
- No authentication required for basic queries
- CORS enabled (`Access-Control-Allow-Origin: *`), so it can be called from a browser
- Stop IDs can be given as numeric VVO IDs (`33000028`) or as DHIDs (`de:14612:28`)
- Real-time data includes delay information, occupancy levels, and service alerts

An OpenAPI 3.1 description of these endpoints is available at [`openapi/webapi.yaml`](../openapi/webapi.yaml).

## Technical Notes

### EFA System Background

VVO uses the EFA (Elektronische Fahrplanauskunft) server software from [MENTZ GmbH](https://www.mentz.net/). This system is also used by many other German transit organizations including:

- [NVBW (Nahverkehrsgesellschaft Baden-Württemberg)](https://www.nvbw.de/)
- [Ruhrbahn](https://www.ruhrbahn.de/)
- [DVB](https://www.dvb.de/)
- [VRR (Verkehrsverbund Rhein-Ruhr)](https://www.vrr.de/)
- [Naldo (Verkehrsverbund Neckar-Alb-Donau)](https://www.naldo.de/)
- [VMS (Verkehrsverbund Mittelsachsen)](https://www.vms.de/)
- [KVV (Karlsruher Verkehrsverbund)](https://www.kvv.de/)
- [Verkehrsverbund Steiermark](https://verbundlinie.at/)

### Date Format

All timestamps in responses use Microsoft JSON date format:

- Format: `/Date(milliseconds+timezone)/`
- Example: `/Date(1487778279147+0100)/`
- The timestamp is in milliseconds since Unix epoch (UTC)
- A timezone offset follows (e.g., +0100 for CET). It is informational only and many fields use `-0000`

### Coordinate System

The API uses GK4 (Gauss-Kruger Zone 4) coordinates for location data. When working with coordinates:

- Right (Rechtswert) and Up (Hochwert) values are used
- These need to be converted for use with standard GPS/WGS84 systems
- The DVB mobile app detects the coordinate system by checking if the value contains a decimal point: if it does, it's treated as WGS84; otherwise GK4

### Rate Limiting and Stability

Community reports indicate:

- Occasional 503 Service Unavailable errors
- Random timeouts may occur
- IP-based restrictions may apply (e.g., TU Dresden network ranges)
- Implement retry logic with exponential backoff
- Cache responses where appropriate

---

# PointFinder

Find stops, addresses, or POIs based on a search query or coordinates.

## Request

GET `https://webapi.vvo-online.de/tr/pointfinder`

The DVB mobil app uses GET with query parameters for this endpoint. The API also accepts POST with a JSON body.

**Important:** The `format=json` parameter is required for GET requests. Without it, the endpoint returns an HTML debug page instead of JSON.

### Query parameters (GET) / JSON body (POST):

| Name            | Type   | Description                                                             | Required |
| --------------- | ------ | ----------------------------------------------------------------------- | -------- |
| `query`         | String | Search query (name or `coord:<lng>:<lat>` in GK4)                       | Yes      |
| `limit`         | Int    | Maximum number of results                                               | No       |
| `stopsOnly`     | Bool   | Only search for stops if `true`                                         | No       |
| `regionalOnly`  | Bool   | Include only stops in VVO area if `true`                                | No       |
| `stopShortcuts` | Bool   | Include stop shortcuts if `true`                                        | No       |
| `assignedstops` | Bool   | Include stops assigned to coordinate if `true` (for coordinate queries) | No       |
| `showlines`     | Bool   | Include line information in results                                     | No       |
| `provider`      | String | Provider filter, default `"dvb"`                                        | No       |
| `format`        | String | Response format, use `"json"`                                           | No       |

For coordinate queries, the format is `coord:<longitude>:<latitude>` in GK4 coordinates.

## Response

```js
{
  "PointStatus": "List",
  "Status": {
    "Code": "Ok"
  },
  "Points": [
    "33000742|||Helmholtzstraße|5655904|4621157|0||",
    "36030083||Chemnitz|Helmholtzstr|5635837|4566835|0||",
    "9022020||Bonn|Helmholtzstraße|0|0|0||"
  ],
  "ExpirationTime": "\/Date(1487859556456+0100)\/"
}
```

```
curl "https://webapi.vvo-online.de/tr/pointfinder?query=helmholtz&stopsOnly=true&format=json"
```

`PointStatus` is `List` for a list of candidates, `Identified` if the query resolved to a single point (the first entry), and `NotIdentified` on errors. A missing `query` returns HTTP 400 with `Status.Code: "ValidationError"`.

Be aware that the elements of the `Points` array can take different forms with different types. If doing a PointFinder request for a coordinate, the first element will look like the following for example `coord:4621022.70:504065.41:NAV4:Nöthnitzer Straße 46|c|(Dresden)|Nöthnitzer Straße 46|5655935|4621022|0||`.

Point strings contain nine values separated by a vertical bar (`|`). As far as we know the values are:

| Index | Type          | Description                                                       | Always included |
| ----- | ------------- | ----------------------------------------------------------------- | --------------- |
| 0     | Int or string | ID of a stop (int), or an other type (string, see below)          | Yes             |
| 1     | String        | Type of point: `a` for streets, `p` for pois, `c` for coordinates | No              |
| 2     | String        | City name if point is not in the VVO area                         | No              |
| 3     | String        | Name of the stop or street                                        | Yes             |
| 4     | Int           | Latitude (GK4 coordinate, or WGS84 if contains ".")               | Yes             |
| 5     | Int           | Longitude (GK4 coordinate, or WGS84 if contains ".")              | Yes             |
| 6     | Int           | Distance in meters when submitting coords in query, otherwise 0   | Yes             |
| 7     | String        | Serving lines, only with `showlines` (see below)                  | No              |
| 8     | String        | Shortcut of the stop, only with `stopShortcuts`                   | No              |

The serving lines field groups lines by a numeric transport type, e.g. `1:3~7~8#2:66~68#5:S1~S2`. Groups are separated by `#`, the type and its lines by `:`, and lines by `~`.

Instead of a numeric ID for a stop, there are other types of ids:

- streetID
- poiID
- suburbID
- placeID
- coords

### Street IDs

Street IDs contain 18 values separated by colons (`:`), for example `streetID:1500002808:46:14612000:-1:Nöthnitzer Straße:Dresden:Nöthnitzer Straße::Nöthnitzer Straße:01187:ANY:DIVA_SINGLEHOUSE:1527615:5374139:MRCV:vvo:0`. As far as we know the values are:

| Index | Type   | Description                                                                                     | Always included |
| ----- | ------ | ----------------------------------------------------------------------------------------------- | --------------- |
| 0     | String | Suffix for streets: `streetID`                                                                  | Yes             |
| 1     | Int    | ID of the street (OMC)                                                                          | Yes             |
| 2     | String | Street number, e.g. for `Musterstraße 42a` it's `42a`                                           | No              |
| 3     | Int    | Unknown                                                                                         | Yes             |
| 4     | Int    | Unknown, but mostly `-1` (invalid value)                                                        | Yes             |
| 5     | String | Street name                                                                                     | Yes             |
| 6     | String | City name                                                                                       | Yes             |
| 7     | String | Street name                                                                                     | Yes             |
| 8     | ???    | Unknown                                                                                         | No              |
| 9     | String | Street name                                                                                     | Yes             |
| 10    | String | Postal code                                                                                     | Yes             |
| 11    | String | `ANY`                                                                                           | Yes             |
| 12    | String | Either `DIVA_STREET` for a complete street or `DIVA_SINGLEHOUSE` for a point with street number | Yes             |
| 13    | Int    | Unknown. Probably right part of coordinates in MDV format                                       | Yes             |
| 14    | Int    | Unknown. Probably up part of coordinates in MDV format                                          | Yes             |
| 15    | String | Map name, e.g. `MRCV` or `NAV4`                                                                 | Yes             |
| 16    | String | Acronym of the transport association, `vvo` or `VVO`                                            | Yes             |
| 17    | Int    | Unknown, observed `0`                                                                           | Yes             |

### POI IDs

POI IDs contain 13 values separated by colons (`:`). As far as we know the values are:

| Index | Type   | Description                                               | Always included |
| ----- | ------ | --------------------------------------------------------- | --------------- |
| 0     | String | Suffix for pois: `poiID`                                  | Yes             |
| 1     | Int    | ID of the poi                                             | Yes             |
| 2     | Int    | Unknown                                                   | Yes             |
| 3     | Int    | Unknown, but mostly `-1` (invalid value)                  | Yes             |
| 4     | String | Name of the poi                                           | Yes             |
| 5     | String | City name                                                 | Yes             |
| 6     | String | Name of the poi                                           | Yes             |
| 7     | String | `ANY`                                                     | Yes             |
| 8     | String | `POI`                                                     | Yes             |
| 9     | Int    | Unknown. Probably right part of coordinates in MDV format | Yes             |
| 10    | Int    | Unknown. Probably up part of coordinates in MDV format    | Yes             |
| 11    | String | Map name, e.g. `MRCV` or `NAV4`                           | Yes             |
| 12    | String | Acronym of the transport association, e.g. `VVO`          | Yes             |

---

# Departure Monitor

List upcoming departures from a given stop.

## Request

POST `https://webapi.vvo-online.de/dm`

### JSON body:

| Name               | Type          | Description                                       | Required |
| ------------------ | ------------- | ------------------------------------------------- | -------- |
| `stopid`           | String        | ID or DHID of the stop                            | Yes      |
| `limit`            | Int           | Maximum number of results                         | No       |
| `time`             | String        | ISO8601 timestamp, e.g. `2017-02-22T15:40:26Z`    | No       |
| `isarrival`        | Bool          | Interpret time as arrival time                    | No       |
| `shorttermchanges` | Bool          | Include short-term route changes                  | No       |
| `mot`              | Array[String] | Allowed [modes of transport](#modes-of-transport) | No       |
| `mentzonly`        | Bool          | Use EFA/Mentz backend only                        | No       |
| `departureid`      | String        | Specific departure ID to query                    | No       |
| `format`           | String        | Response format, use `"json"`                     | No       |

## Response

```js
{
  "Name": "Hauptbahnhof",
  "Status": {
    "Code": "Ok"
  },
  "Place": "Dresden",
  "ExpirationTime": "\/Date(1487778279147+0100)\/",
  "Departures": [
    {
      "Id": "voe:11003: :H:j26",
      "DlId": "de:vvo:11-3",
      "LineName": "3",
      "Direction": "Wilder Mann",
      "Platform": {
        "Name": "3",
        "Type": "Platform"
      },
      "Mot": "Tram",
      "RealTime": "\/Date(1487778230000+0100)\/",
      "ScheduledTime": "\/Date(1487778060000+0100)\/",
      "State": "Delayed",
      "RouteChanges": [
        "509223"
      ],
      "Diva": {
        "Number": "11003",
        "Network": "voe"
      },
      "CancelReasons": [],
      "Occupancy": "Unknown"
    },
    {
      "Id": "voe:11008: :H:j26",
      "DlId": "de:vvo:11-8",
      "LineName": "8",
      "Direction": "Südvorstadt",
      "Platform": {
        "Name": "4",
        "Type": "Platform"
      },
      "Mot": "Tram",
      "RealTime": "\/Date(1487778356000+0100)\/",
      "ScheduledTime": "\/Date(1487778300000+0100)\/",
      "State": "InTime",
      "Diva": {
        "Number": "11008",
        "Network": "voe"
      },
      "Occupancy": "ManySeats"
    }
  ]
}
```

### Response fields (per departure):

| Field           | Type          | Description                                                |
| --------------- | ------------- | ---------------------------------------------------------- |
| `Id`            | String        | Departure ID (use with dm/trip)                            |
| `DlId`          | String        | DHID-style line identifier (e.g. `"de:vvo:11-11"`)         |
| `LineName`      | String        | Line number/name                                           |
| `Direction`     | String        | Destination name                                           |
| `Platform`      | Object        | `Name` (string) and `Type` (`"Platform"` or `"Railtrack"`) |
| `Mot`           | String        | Mode of transport                                          |
| `ScheduledTime` | String        | Planned departure time                                     |
| `RealTime`      | String        | Actual/predicted departure time, missing if cancelled      |
| `State`         | String        | `"InTime"`, `"Delayed"`, or `"Cancelled"`                  |
| `RouteChanges`  | Array[String] | IDs of active route changes affecting this departure       |
| `Diva`          | Object        | `Number` and `Network` identifiers                         |
| `CancelReasons` | Array[Object] | Each with a `Reason` string, if trip is cancelled          |
| `Occupancy`     | String        | `"Unknown"`, `"ManySeats"`, `"StandingOnly"`, or `"Full"`  |

```
curl -X "POST" "https://webapi.vvo-online.de/dm" \
     -H "Content-Type: application/json;charset=UTF-8" \
     -d $'{
  "stopid": "33000028",
  "limit": 2,
  "mot": [
    "Tram",
    "CityBus",
    "IntercityBus",
    "SuburbanRailway",
    "Train",
    "Cableway",
    "Ferry",
    "HailedSharedTaxi"
  ],
  "format": "json"
}'
```

An unknown stop returns HTTP 200 with `"Status": {"Code": "ServiceError", "Message": "stop invalid"}` and no `Departures`. A known stop that no line currently serves, e.g. because of construction, returns the same code with `"Message": "no serving lines found"`, together with its `Name` and `Place`.

---

# Trip Details

Get details about the stations involved in a particular trip.

## Request

POST `https://webapi.vvo-online.de/dm/trip`

### JSON body:

| Name        | Type   | Description                                                     | Required |
| ----------- | ------ | --------------------------------------------------------------- | -------- |
| `tripid`    | String | The "Id" from a departure monitor response (Departures[\*].Id)  | Yes      |
| `time`      | String | Timestamp in `/Date(...)/ ` format from the departure response  | Yes      |
| `stopid`    | String | ID of a stop in the route (marked Position=Current in response) | Yes      |
| `isarrival` | Bool   | Interpret time as arrival                                       | No       |
| `mapdata`   | Bool   | Include map coordinate data in response                         | No       |
| `format`    | String | Response format, use `"json"`                                   | No       |

```
curl -X "POST" "https://webapi.vvo-online.de/dm/trip" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -d $'{
  "tripid": "voe:11011: :H:j26",
  "time": "/Date(1791464640000-0000)/",
  "stopid": "33000293",
  "mapdata": true,
  "format": "json"
}'
```

## Response

```json
{
  "Stops": [
    {
      "Id": "33000294",
      "DhId": "de:14612:294",
      "Place": "",
      "Name": "Dresden Angelikastraße",
      "Longitude": 4625079,
      "Latitude": 5660615,
      "Position": "Previous",
      "Platform": {
        "Name": "1",
        "Type": "Platform"
      },
      "Time": "/Date(1791463560000-0000)/",
      "RealTime": "/Date(1791463560000-0000)/",
      "State": "InTime",
      "Occupancy": "Unknown"
    },
    {
      "Id": "33000293",
      "DhId": "de:14612:293",
      "Place": "",
      "Name": "Dresden Waldschlößchen",
      "Longitude": 4624656,
      "Latitude": 5660652,
      "Position": "Current",
      "Platform": {
        "Name": "1",
        "Type": "Platform"
      },
      "Time": "/Date(1791463680000-0000)/",
      "RealTime": "/Date(1791463740000-0000)/",
      "State": "Delayed",
      "Occupancy": "ManySeats"
    }
  ],
  "Status": {
    "Code": "Ok"
  },
  "MapData": ["Tram|5660211|4630082|5660194|4630066|..."]
}
```

### Stop fields:

| Field           | Type          | Description                                               |
| --------------- | ------------- | --------------------------------------------------------- |
| `Id`            | String        | Stop ID                                                   |
| `DhId`          | String        | DHID of the stop, e.g. `"de:14612:293"`                   |
| `Place`         | String        | City name, often empty with the city included in `Name`   |
| `Name`          | String        | Stop name                                                 |
| `Position`      | String        | `"Previous"`, `"Current"`, `"Next"`, or `"Onward"`        |
| `Platform`      | Object        | `Name` and `Type` (`"Platform"` or `"Railtrack"`)         |
| `Time`          | String        | Scheduled time                                            |
| `RealTime`      | String        | Actual/predicted time (if available)                      |
| `State`         | String        | Real-time state (e.g. `"InTime"`)                         |
| `CancelReasons` | Array[Object] | Each with `Reason` string, if stop is skipped             |
| `Latitude`      | Int           | GK4 latitude                                              |
| `Longitude`     | Int           | GK4 longitude                                             |
| `Occupancy`     | String        | `"Unknown"`, `"ManySeats"`, `"StandingOnly"`, or `"Full"` |

The `MapData` field (only with `mapdata: true`) is an array of pipe-delimited GK4 coordinate lists for drawing the route on a map, each prefixed by the transport mode (sometimes `Undefined`).

## Run identity, or: what `tripid` and `time` actually select

- `tripid` does not identify a single run. It names a line's course and is shared by every run of that line and direction, meaning all "3 Wilder Mann" departures report the same Id (currently of the form `voe:11003: :H:j26`, where `H`/`R` is the direction and `j26` the timetable year).
- The actual run is selected by `time`: the endpoint returns the run with the next departure at `stopid` at or after `time`, matched against **realtime** (not scheduled) departure times.
- Future realtimes jitter. A token equal to the run's expected departure at a stop stops matching that run the moment the prediction shifts a minute earlier, and the same query silently returns the line's _next_ run.
- Past realtimes are frozen. A token slightly before a departure that already happened keeps identifying the same run indefinitely. Runs that have long left the stop (or even reached their terminus) are still returned.
- `Stops` is not limited to one journey: it is a sliding window over the course's whole service (roughly 1.5–2 h of chained journeys, including terminus loops), so the same stop can appear multiple times. Disambiguate occurrences by their scheduled `Time`; `Position` marks the occurrence the query matched.

To reliably poll one run over time, keep `stopid` and `time` fixed, e.g. the stop you care about with a token a minute or two before the run's departure there and verify each response by the scheduled `Time` at that stop, which never changes for a given run. Any strategy that refreshes the token from realtime data eventually drifts onto the next run.

---

# Query a Trip

Plan a journey between two stops.

## Request

POST `https://webapi.vvo-online.de/tr/trips`

### JSON body

| Name               | Type   | Description                                             | Required |
| ------------------ | ------ | ------------------------------------------------------- | -------- |
| `origin`           | String | Stop ID, or a street/POI/coordinate ID from PointFinder | Yes      |
| `destination`      | String | Same as `origin`                                        | Yes      |
| `time`             | String | ISO8601 timestamp                                       | No       |
| `isarrivaltime`    | Bool   | Is `time` arrival or departure                          | No       |
| `shorttermchanges` | Bool   | Include short-term route changes                        | No       |
| `via`              | String | Stop ID for an intermediate waypoint                    | No       |
| `mobilitySettings` | Object | Accessibility preferences (see below)                   | No       |
| `standardSettings` | Object | Journey preferences (see below)                         | No       |
| `format`           | String | Response format, use `"json"`                           | No       |

### `mobilitySettings` object

| Field                 | Type   | Values                                         | Description                                                                                               |
| --------------------- | ------ | ---------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `mobilityRestriction` | String | `"None"`, `"Medium"`, `"High"`, `"Individual"` | None = no restriction, Medium = walking impaired, High = unaided wheelchair, Individual = custom settings |
| `solidStairs`         | Bool   |                                                | Allow solid stairs (Individual mode)                                                                      |
| `escalators`          | Bool   |                                                | Allow escalators (Individual mode)                                                                        |
| `leastChange`         | Bool   |                                                | Prefer fewest changes (Individual mode)                                                                   |
| `entrance`            | String | `"Any"`, `"SmallStep"`, `"NoStep"`             | Vehicle entrance requirement (Individual mode)                                                            |

### `standardSettings` object

| Field                     | Type          | Values                                                     | Description                            |
| ------------------------- | ------------- | ---------------------------------------------------------- | -------------------------------------- |
| `mot`                     | Array[String] | See [Modes of Transport](#modes-of-transport)              | Allowed transport modes                |
| `maxChanges`              | String        | `"Unlimited"`, `"Two"`, `"One"`, `"None"`                  | Maximum number of transfers            |
| `walkingSpeed`            | String        | `"VerySlow"`, `"Slow"`, `"Normal"`, `"Fast"`, `"VeryFast"` | Walking speed preference               |
| `footpathToStop`          | Int           |                                                            | Max walking distance to stop (minutes) |
| `includeAlternativeStops` | Bool          |                                                            | Include nearby alternative stops       |
| `extraCharge`             | String        | `""`, `"None"`, `"LocalTraffic"`                           | Extra charge filter                    |

```bash
curl -X "POST" "https://webapi.vvo-online.de/tr/trips" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -d $'{
  "origin": "33000028",
  "destination": "33000016",
  "time": "2017-12-08T21:36:42.775Z",
  "isarrivaltime": false,
  "shorttermchanges": true,
  "mobilitySettings": {
    "mobilityRestriction": "None"
  },
  "standardSettings": {
    "footpathToStop": 5,
    "includeAlternativeStops": true,
    "maxChanges": "Unlimited",
    "walkingSpeed": "Normal",
    "mot": [
      "Tram", "CityBus", "IntercityBus", "SuburbanRailway",
      "Train", "Cableway", "Ferry", "HailedSharedTaxi"
    ]
  },
  "format": "json"
}'
```

## Response

```json
{
  "SessionId": "2065107265:efa3",
  "Status": {
    "Code": "Ok"
  },
  "StandardSettingsActive": true,
  "Routes": [
    {
      "PriceLevel": 1,
      "Price": "3,60",
      "PriceDayTicket": "9,50",
      "TicketNotes": "",
      "Net": "voe",
      "Duration": 7,
      "Interchanges": 0,
      "MotChain": [
        {
          "DlId": "de:vvo:10-1",
          "StatelessId": "ddb:92D01: :R:j26",
          "Type": "RapidTransit",
          "Name": "S1",
          "Direction": "Meißen S-Bf. Triebischtal",
          "Changes": [],
          "Diva": {
            "Number": "92D01",
            "Network": "ddb"
          },
          "TransportationCompany": "DB Regio AG Südost",
          "OperatorCode": "8004",
          "ProductName": "S-Bahn",
          "TrainNumber": "30728"
        }
      ],
      "NumberOfFareZones": "1 Tarifzone",
      "NumberOfFareZonesDayTicket": "1 Tarifzone",
      "FareZoneNames": "TZ Dresden (10)",
      "FareZoneNamesDayTicket": "TZ Dresden (10)",
      "FareZoneOrigin": 10,
      "FareZoneDestination": 10,
      "RouteId": 0,
      "PartialRoutes": [
        {
          "PartialRouteId": 0,
          "Duration": 7,
          "Mot": {
            "DlId": "de:vvo:10-1",
            "StatelessId": "ddb:92D01: :R:j26",
            "Type": "RapidTransit",
            "Name": "S1",
            "Direction": "Meißen S-Bf. Triebischtal",
            "Changes": [],
            "Diva": {
              "Number": "92D01",
              "Network": "ddb"
            },
            "TransportationCompany": "DB Regio AG Südost",
            "OperatorCode": "8004",
            "ProductName": "S-Bahn",
            "TrainNumber": "30728"
          },
          "MapDataIndex": 0,
          "Shift": "None",
          "Infos": ["Fahrradmitnahme begrenzt möglich"],
          "RegularStops": [
            {
              "ArrivalTime": "/Date(1791465000000-0000)/",
              "DepartureTime": "/Date(1791465000000-0000)/",
              "ArrivalRealTime": "/Date(1791465000000-0000)/",
              "DepartureRealTime": "/Date(1791465060000-0000)/",
              "Place": "Dresden",
              "Name": "Hauptbahnhof",
              "Type": "Stop",
              "DataId": "33000028",
              "DhId": "de:14612:28",
              "Platform": {
                "Name": "14",
                "Type": "Railtrack"
              },
              "Latitude": 5657622,
              "Longitude": 4621566,
              "DepartureState": "Delayed",
              "ArrivalState": "InTime",
              "CancelReasons": [],
              "ParkAndRail": [],
              "Occupancy": "Unknown",
              "BikeAndRideBoxes": []
            },
            {
              "ArrivalTime": "/Date(1791465360000-0000)/",
              "DepartureTime": "/Date(1791465360000-0000)/",
              "Place": "Dresden",
              "Name": "Bahnhof Neustadt",
              "Type": "Stop",
              "DataId": "33000016",
              "DhId": "de:14612:16",
              "Platform": {
                "Name": "1",
                "Type": "Railtrack"
              },
              "Latitude": 5660412,
              "Longitude": 4622148,
              "CancelReasons": [],
              "ParkAndRail": [],
              "Occupancy": "Unknown",
              "BikeAndRideBoxes": []
            }
          ],
          "NextDepartureTimes": ["/Date(1791466200000-0000)/"],
          "PreviousDepartureTimes": []
        }
      ],
      "MapData": ["RapidTransit|5657588|4621635|5657675|4621458|..."],
      "Tickets": [
        {
          "Name": "VVO Einzelfahrt",
          "PriceLevel": 1,
          "Price": "3,60",
          "NumberOfFareZones": "1 Tarifzone",
          "FareZoneNames": "TZ Dresden (10)"
        }
      ]
    }
  ]
}
```

A failed calculation returns HTTP 200 with a `Status.Code` other than `Ok`, e.g. `"ServiceError"` with `"Message": "stop invalid"`, and no `Routes`.

### Route-level fields:

| Field                        | Type          | Description                                                                                    |
| ---------------------------- | ------------- | ---------------------------------------------------------------------------------------------- |
| `RouteId`                    | Int           | Route identifier, starting at 0                                                                |
| `Duration`                   | Int           | Total duration in minutes                                                                      |
| `Interchanges`               | Int           | Number of transfers                                                                            |
| `Price`                      | String        | Single ticket price in euros, e.g. `"3,60"`                                                    |
| `PriceDayTicket`             | String        | Day ticket price in euros                                                                      |
| `PriceLevel`                 | Int           | Price level                                                                                    |
| `TicketNotes`                | String        | Notes on tickets, usually empty                                                                |
| `Net`                        | String        | Network, e.g. `"voe"`, may be empty                                                            |
| `FareZoneOrigin`             | Int           | Origin fare zone number                                                                        |
| `FareZoneDestination`        | Int           | Destination fare zone number                                                                   |
| `FareZoneNames`              | String        | Human-readable zone names, e.g. `"TZ Dresden (10)"`                                            |
| `FareZoneNamesDayTicket`     | String        | Zone names for the day ticket                                                                  |
| `NumberOfFareZones`          | String        | Number of fare zones as text, e.g. `"1 Tarifzone"`                                             |
| `NumberOfFareZonesDayTicket` | String        | Same for the day ticket                                                                        |
| `RouteCancelled`             | Bool          | Whether the entire route is cancelled (not always present)                                     |
| `MapData`                    | Array[String] | Pipe-delimited GK4 coordinate strings, prefixed with transport mode                            |
| `MotChain`                   | Array[Object] | Summary of transport modes used, same shape as a leg's `Mot`                                   |
| `PartialRoutes`              | Array[Object] | Individual legs of the journey                                                                 |
| `Tickets`                    | Array[Object] | Available tickets with `Name`, `PriceLevel`, `Price`, `NumberOfFareZones`, and `FareZoneNames` |

The response also contains `SessionId` for use with [tr/prevnext](#earlierlater-connections), [tr/prevnextmove](#alternative-connection-for-a-leg) and [tr/trippdf](#trip-pdf-export), and `StandardSettingsActive`/`MobilitySettingsActive` flags.

### PartialRoute fields:

| Field                    | Type          | Description                                                          |
| ------------------------ | ------------- | -------------------------------------------------------------------- |
| `PartialRouteId`         | Int           | Leg identifier, missing for some footpaths                           |
| `Duration`               | Int           | Leg duration in minutes, missing for some accessibility segments     |
| `MapDataIndex`           | Int           | Index into the route's MapData array                                 |
| `Shift`                  | String        | Shift indicator, usually `"None"`                                    |
| `Infos`                  | Array[String] | Additional information, e.g. bicycle rules (not always present)      |
| `Mot`                    | Object        | Transport mode details for this leg (see below)                      |
| `RegularStops`           | Array[Object] | Stops of this leg, missing for short transfer footpaths              |
| `NextDepartureTimes`     | Array[String] | Later departures of this leg                                         |
| `PreviousDepartureTimes` | Array[String] | Earlier departures of this leg                                       |
| `TripCancelled`          | Bool          | Whether this leg is cancelled (not always present)                   |
| `ChangeoverEndangered`   | Bool          | Whether the transfer to the next leg is at risk (not always present) |
| `BookingLink`            | String        | Service hotline URL for on-demand services (not always present)      |

The `Mot` object has a `Type` (see [Modes of Transport](#modes-of-transport), e.g. `"Footpath"` for walking) and, for vehicles, `Name`, `Direction`, `DlId`, `StatelessId` (the line course ID also used by [dm/trip](#trip-details)), `Changes` (route change IDs), `Diva`, `TransportationCompany`, `OperatorCode`, `ProductName`, and `TrainNumber`. Footpaths have empty strings in most of these.

### RegularStop fields:

| Field               | Type          | Description                                                                               |
| ------------------- | ------------- | ----------------------------------------------------------------------------------------- |
| `DataId`            | String        | Stop ID, or a street/POI ID for the first and last point                                  |
| `DhId`              | String        | DHID of the stop, empty for non-stops                                                     |
| `Name`              | String        | Stop name                                                                                 |
| `Place`             | String        | City name                                                                                 |
| `Type`              | String        | `"Stop"` or `"Address"`                                                                   |
| `Platform`          | Object        | `Name` and `Type` (`"Platform"` or `"Railtrack"`)                                         |
| `Latitude`          | Int           | GK4 latitude                                                                              |
| `Longitude`         | Int           | GK4 longitude                                                                             |
| `ArrivalTime`       | String        | Scheduled arrival                                                                         |
| `DepartureTime`     | String        | Scheduled departure                                                                       |
| `ArrivalRealTime`   | String        | Actual/predicted arrival (if real-time data available)                                    |
| `DepartureRealTime` | String        | Actual/predicted departure (if real-time data available)                                  |
| `ArrivalState`      | String        | Real-time state for arrival                                                               |
| `DepartureState`    | String        | Real-time state for departure                                                             |
| `CancelReasons`     | Array[Object] | Each with a `Reason` string                                                               |
| `ParkAndRail`       | Array[Object] | P+R facilities with `Name`, `Coordinates`, `FreeSpaces`, `TotalSpaces`, and `ParkingLots` |
| `BikeAndRideBoxes`  | Array         | Bike boxes, observed empty                                                                |
| `Occupancy`         | String        | `"Unknown"`, `"ManySeats"`, `"StandingOnly"`, or `"Full"`                                 |

---

# Earlier/Later Connections

Paginate trip results using the session ID from a previous `tr/trips` response.

## Request

POST `https://webapi.vvo-online.de/tr/prevnext`

### JSON body

| Name               | Type   | Description                                       | Required |
| ------------------ | ------ | ------------------------------------------------- | -------- |
| `origin`           | String | Stop ID of start station                          | Yes      |
| `destination`      | String | Stop ID of destination station                    | Yes      |
| `sessionId`        | String | Session ID from tr/trips response                 | Yes      |
| `time`             | String | ISO8601 timestamp                                 | No       |
| `isarrivaltime`    | Bool   | Is `time` arrival or departure                    | No       |
| `shorttermchanges` | Bool   | Include short-term route changes                  | No       |
| `via`              | String | Stop ID for intermediate waypoint                 | No       |
| `mobilitySettings` | Object | See [tr/trips](#query-a-trip)                     | No       |
| `standardSettings` | Object | See [tr/trips](#query-a-trip)                     | No       |
| `previous`         | Bool   | `true` for earlier, `false` for later connections | Yes      |
| `numberprev`       | Int    | Number of previous results (usually `0`)          | No       |
| `numbernext`       | Int    | Number of next results (usually `0`)              | No       |
| `format`           | String | Response format, use `"json"`                     | No       |

## Response

Same structure as [tr/trips](#query-a-trip) response, including a `SessionId` for continued pagination. `Routes` contains the previously returned routes plus the newly loaded ones.

---

# Alternative Connection for a Leg

Get an alternative connection for a specific partial route (leg) of a trip.

## Request

POST `https://webapi.vvo-online.de/tr/prevnextmove`

### JSON body

| Name               | Type   | Description                                       | Required |
| ------------------ | ------ | ------------------------------------------------- | -------- |
| `origin`           | String | Stop ID of start station                          | Yes      |
| `destination`      | String | Stop ID of destination station                    | Yes      |
| `sessionid`        | String | Session ID from tr/trips response                 | Yes      |
| `routeid`          | String | Route ID to modify                                | Yes      |
| `partialrouteid`   | String | Partial route ID to replace                       | Yes      |
| `time`             | String | ISO8601 timestamp                                 | No       |
| `via`              | String | Stop ID for intermediate waypoint                 | No       |
| `mobilitySettings` | Object | See [tr/trips](#query-a-trip)                     | No       |
| `standardSettings` | Object | See [tr/trips](#query-a-trip)                     | No       |
| `previous`         | Bool   | `true` for earlier, `false` for later alternative | Yes      |
| `format`           | String | Response format, use `"json"`                     | No       |

## Response

Same structure as [tr/trips](#query-a-trip) response. If no alternative exists for the leg (e.g. for a single-leg route), the response has `"Status": {"Code": "ServiceError", "Message": "trip calculation error"}`.

---

# Trip PDF Export

Generate a PDF document for a planned trip.

## Request

GET `https://webapi.vvo-online.de/tr/trippdf`

All parameters are passed as query string parameters.

| Name               | Type   | Description                       | Required |
| ------------------ | ------ | --------------------------------- | -------- |
| `id`               | String | `RouteId` from tr/trips           | Yes      |
| `origin`           | String | Stop ID of start station          | Yes      |
| `destination`      | String | Stop ID of destination station    | Yes      |
| `sessionid`        | String | Session ID from tr/trips response | Yes      |
| `time`             | String | ISO8601 timestamp                 | No       |
| `isarrivaltime`    | Bool   | Is `time` arrival or departure    | No       |
| `via`              | String | Stop ID for intermediate waypoint | No       |
| `mobilitysettings` | String | JSON string of mobility settings  | No       |
| `standardSettings` | String | JSON string of standard settings  | No       |
| `numberprev`       | Int    | Usually `0`                       | No       |
| `numbernext`       | Int    | Usually `0`                       | No       |
| `format`           | String | Use `"json"`                      | No       |

```
curl "https://webapi.vvo-online.de/tr/trippdf?id=1&origin=33000028&destination=33000016&sessionid=367417461:efa4&time=2017-12-08T21:36:42.775Z&isarrivaltime=false&numberprev=0&numbernext=0&format=json"
```

The response is an `application/pdf` attachment named `trip.pdf`. Missing parameters return HTTP 400 with a JSON `ValidationError` status.

---

# Route Changes

Get information about route changes due to construction work or disruptions.

## Request

POST `https://webapi.vvo-online.de/rc`

### JSON body

| Name        | Type   | Description                   | Required |
| ----------- | ------ | ----------------------------- | -------- |
| `shortterm` | Bool   | Include short-term changes    | No       |
| `provider`  | String | Provider filter               | No       |
| `format`    | String | Response format, use `"json"` | No       |

```bash
curl -X "POST" "https://webapi.vvo-online.de/rc" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -d $'{ "shortterm": true, "format": "json" }'
```

## Response

```json
{
  "Changes": [
    {
      "Id": "27670",
      "Type": "Scheduled",
      "Title": "Instandhaltungsmaßnahmen zwischen Oschatz und Riesa",
      "Description": "<h2>Beschreibung</h2><p>...</p>",
      "ValidityPeriods": [
        {
          "Begin": "/Date(1791486000000-0000)/",
          "End": "/Date(1791500400000-0000)/"
        }
      ],
      "LineIds": ["90D50:ddb"],
      "PublishDate": "/Date(1789729260000-0000)/",
      "SeqID": "306507661"
    }
  ],
  "Banners": [],
  "Lines": [
    {
      "Id": "11001:voe",
      "Diva": {
        "Number": "11001",
        "Network": "voe"
      },
      "Name": "1",
      "RouteDescription": "Dresden Prohlis Gleisschleife - Dresden Waltherstraße",
      "TransportationCompany": "DVB",
      "Mot": "Tram",
      "Divas": [{ "Number": "11001", "Network": "voe" }],
      "Changes": ["27721", "27769", "27668"]
    }
  ],
  "Status": {
    "Code": "Ok"
  },
  "ExpirationTime": "/Date(1791465272750+0200)/"
}
```

### Change fields:

| Field                | Type          | Description                                                     |
| -------------------- | ------------- | --------------------------------------------------------------- |
| `Id`                 | String        | Disruption ID                                                   |
| `SeqID`              | String        | Sequence/version number                                         |
| `Title`              | String        | Short description                                               |
| `Summary`            | String        | One-line summary (not always present)                           |
| `Description`        | String        | HTML-formatted detailed description                             |
| `Topic`              | String        | Topic, often empty (not always present)                         |
| `Type`               | String        | `"Scheduled"` (planned construction) or disruption type         |
| `TripRequestInclude` | Bool          | Whether this affects trip planning results (not always present) |
| `PublishDate`        | String        | When the change was published                                   |
| `LineIds`            | Array[String] | Affected line IDs, matching `Lines[].Id`                        |
| `ValidityPeriods`    | Array[Object] | Each with a `Begin` and an optional `End` timestamp             |

The response also includes `Banners` (general announcements, filter by `Type: "MobileWebsite"`; empty when last checked) and `Lines`. Each line has an `Id` of the form `<DIVA number>:<network>`, `Name`, `Mot`, `RouteDescription`, `TransportationCompany`, `Diva`, `Divas`, and `Changes` (the IDs of its changes).

The response is large (over 200 kB).

Note: HTML in `Description` may include inline styles like `<font color="#abc" />`.

---

# Route Change Lines

Get a list of lines with their identifiers. This list is longer than the `Lines` of [Route Changes](#route-changes) (414 vs. 188 lines when last checked), so it seems to cover the whole network rather than only lines with active changes.

## Request

POST `https://webapi.vvo-online.de/rc/lines`

### JSON body

| Name       | Type   | Description                   | Required |
| ---------- | ------ | ----------------------------- | -------- |
| `provider` | String | Provider filter               | No       |
| `format`   | String | Response format, use `"json"` | No       |

## Response

```json
{
  "Lines": [
    {
      "Id": "11001:voe",
      "Diva": {
        "Number": "11001",
        "Network": "voe"
      },
      "Name": "1",
      "RouteDescription": "Dresden Betriebshof Waltherstraße",
      "TransportationCompany": "DVB",
      "Mot": "Tram",
      "Divas": [{ "Number": "11001", "Network": "voe" }],
      "DorisId": "386"
    }
  ],
  "Status": {
    "Code": "Ok"
  },
  "ExpirationTime": "/Date(1791534909187+0200)/"
}
```

`DorisId` is missing for some lines.

---

# Lines

Get information about which lines service a station.

## Request

POST `https://webapi.vvo-online.de/stt/lines`

### JSON body

| Name     | Type   | Description                   | Required |
| -------- | ------ | ----------------------------- | -------- |
| `stopid` | String | ID or DHID of the stop        | Yes      |
| `format` | String | Response format, use `"json"` | No       |

```bash
curl -X "POST" "https://webapi.vvo-online.de/stt/lines" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -d $'{ "stopid": "33000293", "format": "json" }'
```

## Response

```json
{
  "Lines": [
    {
      "Name": "41",
      "Mot": "Tram",
      "Changes": ["5482", "5480", "5481"],
      "Directions": [
        {
          "Name": "Dresden Südvorstadt",
          "TimeTables": [
            {
              "Id": "voe:11041: :H:j19:2",
              "Name": "Ferienfahrplan - gültig vom 06.07. bis 18.08.2019"
            }
          ]
        },
        {
          "Name": "Dresden Bühlau Ullersdorfer Platz",
          "TimeTables": [
            {
              "Id": "voe:11041: :R:j19:2",
              "Name": "Ferienfahrplan - gültig vom 06.07. bis 18.08.2019"
            }
          ]
        }
      ],
      "Diva": {
        "Number": "11041",
        "Network": "voe"
      }
    }
  ],
  "Status": {
    "Code": "Ok"
  },
  "ExpirationTime": "/Date(1563544805289+0200)/"
}
```

`Changes` (route change IDs) is only present for lines with active changes.

---

# Map Pins

Get map markers/pins for stops, POIs, and other points of interest within a bounding box.

## Request

POST `https://webapi.vvo-online.de/map/pins`

### JSON body

| Name       | Type          | Description                   | Required |
| ---------- | ------------- | ----------------------------- | -------- |
| `swlat`    | Int or String | Southwest latitude (GK4)      | Yes      |
| `swlng`    | Int or String | Southwest longitude (GK4)     | Yes      |
| `nelat`    | Int or String | Northeast latitude (GK4)      | Yes      |
| `nelng`    | Int or String | Northeast longitude (GK4)     | Yes      |
| `pintypes` | Array[String] | Types of pins to include      | Yes      |
| `format`   | String        | Response format, use `"json"` | No       |

Bounding box coordinates must be in GK4 format. Convert from WGS84 before sending.

### Pin types:

| Value           | Description              |
| --------------- | ------------------------ |
| `Stop`          | Transit stops            |
| `Platform`      | Individual platforms     |
| `Poi`           | Points of interest       |
| `RentABike`     | Bike rental stations     |
| `CarSharing`    | Car sharing stations     |
| `TicketMachine` | Ticket vending machines  |
| `ParkAndRide`   | Park and ride facilities |

## Response

```json
{
  "Pins": [
    "de:14612:28|||Hauptbahnhof|5657517|4621643||",
    "de:14612:28:2:3|pf||Hauptbahnhof|5657497|4621685|3|",
    "poiID:2104107859:14612000:-1:P+R Dresden Reick:Dresden:P+R Dresden Reick:ANY:POI:1535129:5374992:MRCV:VVO|pr||P+R Dresden Reick|5655506|4625718|21 Stellplätze|"
  ],
  "Status": {
    "Code": "Ok"
  },
  "ExpirationTime": "/Date(1791479635371+0200)/"
}
```

Pin strings are pipe-delimited, similar to [PointFinder](#pointfinder) results:

| Index | Description                                                 |
| ----- | ----------------------------------------------------------- |
| 0     | ID: a DHID for stops and platforms, a POI ID for other pins |
| 1     | Pin type (see below)                                        |
| 2     | City name, usually empty                                    |
| 3     | Name                                                        |
| 4     | Latitude (GK4, may contain decimals)                        |
| 5     | Longitude (GK4, may contain decimals)                       |
| 6     | Extra info: platform name, or capacity for P+R              |

| Type code | Type           |
| --------- | -------------- |
| (empty)   | Stop           |
| `pf`      | Platform       |
| `pr`      | Park and Ride  |
| `p`       | POI            |
| `r`       | Rent a Bike    |
| `t`       | Ticket Machine |
| `c`       | Car Sharing    |

---

# Tariff Zone Polygons

Get polygon boundaries for all VVO tariff zones.

## Request

POST `https://webapi.vvo-online.de/map/polygons`

### JSON body

| Name     | Type   | Description                   | Required |
| -------- | ------ | ----------------------------- | -------- |
| `format` | String | Response format, use `"json"` | No       |

## Response

```json
{
  "Status": {
    "Code": "Ok"
  },
  "ExpirationTime": "/Date(1791621306238+0200)/",
  "Polygons": [
    "93|Elsterwerda|ECECEE|5704015|4605526|5700452|4602883|5701129|4603602|..."
  ]
}
```

Polygon strings are pipe-delimited:

| Index | Description                                                                 |
| ----- | --------------------------------------------------------------------------- |
| 0     | Zone number                                                                 |
| 1     | Zone name                                                                   |
| 2     | Display color (hex, without `#`)                                            |
| 3-4   | Center point latitude and longitude (GK4)                                   |
| 5+    | Alternating latitude and longitude pairs forming the polygon boundary (GK4) |

---

# Cloud Profile Service

The DVB mobil app uses a cloud profile service at `https://m.dvb.de` to sync user favorites and settings across devices.

## Endpoints

| Endpoint            | Method | Description               |
| ------------------- | ------ | ------------------------- |
| `/createprofile`    | POST   | Create a new user profile |
| `/getProfile`       | POST   | Retrieve profile by hash  |
| `/updateprofile`    | POST   | Update profile data       |
| `/deleteprofile`    | POST   | Delete a profile          |
| `/share`            | POST   | Share trip or stop data   |
| `/getshared/<hash>` | GET    | Retrieve shared data      |

Profile data is compressed using `lz-string` (`compressToUTF16`/`decompressFromUTF16`).

### Create Profile payload:

```json
{
  "date": "<timestamp>",
  "email": "<email>",
  "startpage": "<preference>",
  "mot_connection": [],
  "mot_timetable": [],
  "mot_trafficmessages": [],
  "mobility_preferences": {},
  "subscribed_lines": [],
  "point_favorites": [],
  "memo_positions": [],
  "last_connection_settings": {},
  "last_timetables_settings": {}
}
```

Response codes include `"PROFILE_ALREADY_EXISTS"`, `"GET_PROFILE_DATA_OK"`, `"UPDATE_PROFILE_OK"`, `"DELETE_PROFILE_OK"`, `"SHARE_DATA_OK"`.

---

# Schutzengel (Trip Guardian)

The DVB mobil app integrates the Fraunhofer IVI "Schutzengel" (Guardian Angel) API for trip monitoring and real-time travel assistance.

- **Proxy URL:** `https://m.dvb.de/schutzengel/`
- **Backend:** `https://schutzengel.ivi.fraunhofer.de/api/`

This service allows users to register travel plans and receive real-time notifications about delays, missed connections, or disruptions during their journey.

### Key features:

- Anonymous account creation with token-based authentication
- Travel plan creation with multi-leg journeys
- Real-time trip monitoring with position interpolation along polylines
- Push notifications via Firebase Cloud Messaging
- Automatic 60-second sync cycle

### Authentication:

- `POST api/create-account` returns a plain-text token
- Token stored as `schutzengel_auth_token` in localStorage
- All subsequent requests include `Authentication: Bearer <token>` header
- Note: Uses the non-standard header name `Authentication` (not `Authorization`)

### Main endpoints:

| Endpoint              | Method | Description                                          |
| --------------------- | ------ | ---------------------------------------------------- |
| `api/create-account`  | POST   | Create anonymous account, returns auth token         |
| `serverTime`          | GET    | Server timestamp for clock synchronization           |
| `plans`               | POST   | Create a new monitored travel plan                   |
| `plansMinimal`        | GET    | List all plans (minimal data)                        |
| `planRawData`         | GET    | Get full raw data for a plan (`?plan_id=<id>`)       |
| `planRealtime`        | GET    | Get real-time data for active trip (`?trip_id=<id>`) |
| `notifications`       | GET    | Get trip notifications (`?trip_id=<id>`)             |
| `planSetOptions`      | POST   | Update plan notification settings                    |
| `activatePlan`        | POST   | Activate a deactivated plan                          |
| `deactivatePlan`      | POST   | Deactivate an active plan                            |
| `plan`                | DELETE | Delete a single plan                                 |
| `allPlans`            | DELETE | Delete all plans                                     |
| `register-firebase`   | POST   | Register FCM token for push notifications            |
| `unregister-firebase` | POST   | Unregister FCM token                                 |
| `migrate-into-user`   | POST   | Merge anonymous account data into another user       |

---

# Modes of Transport

The API uses string identifiers for modes of transport. The core values accepted by most endpoints are:

| Value              | Description                             |
| ------------------ | --------------------------------------- |
| `Tram`             | Tram/Straßenbahn                        |
| `CityBus`          | City bus (Stadtbus)                     |
| `IntercityBus`     | Intercity/regional bus                  |
| `SuburbanRailway`  | S-Bahn                                  |
| `Train`            | Train (Zug)                             |
| `Cableway`         | Cable car/funicular (Seil-/Schwebebahn) |
| `Ferry`            | Ferry (Fähre)                           |
| `HailedSharedTaxi` | On-demand shared taxi (Rufbus/AST)      |

Additional values that may appear in responses (e.g., in trip results):

| Value                   | Description                                         |
| ----------------------- | --------------------------------------------------- |
| `Bus`                   | Generic bus                                         |
| `RegioBus`              | Regional bus                                        |
| `PlusBus`               | PlusBus service                                     |
| `CitizenBus`            | Citizen bus (Bürgerbus)                             |
| `DemandBus`             | On-demand bus                                       |
| `SchoolBus`             | School bus                                          |
| `ClockBus`              | Clock/scheduled bus (Taktbus)                       |
| `Cablecar`              | Cable car (alias for Cableway)                      |
| `OverheadRailway`       | Overhead/suspension railway                         |
| `RapidTransit`          | Rapid transit (alias for SuburbanRailway)           |
| `Taxi`                  | Taxi                                                |
| `BusOnRequest`          | Night line / on-request bus                         |
| `Footpath`              | Walking segment (in trip results)                   |
| `StayForConnection`     | Wait for transfer (in trip results)                 |
| `StayInVehicle`         | Stay in vehicle / through service (in trip results) |
| `MobilityStairsUp`      | Accessibility: stairs up                            |
| `MobilityStairsDown`    | Accessibility: stairs down                          |
| `MobilityElevatorUp`    | Accessibility: elevator up                          |
| `MobilityElevatorDown`  | Accessibility: elevator down                        |
| `MobilityEscalatorUp`   | Accessibility: escalator up                         |
| `MobilityEscalatorDown` | Accessibility: escalator down                       |
| `MobilityRampUp`        | Accessibility: ramp up                              |
| `MobilityRampDown`      | Accessibility: ramp down                            |

### Platform types

Platform objects in responses use a `Type` field:

- `"Platform"` - Standard platform
- `"Railtrack"` - Railway track/platform

---

# Error Handling

All endpoints return a status object in the response:

```json
{
  "Status": {
    "Code": "Ok"
  }
}
```

On errors, `Status` also has a `Message`:

```json
{
  "Status": {
    "Code": "ValidationError",
    "Message": "stopid has to be not null"
  }
}
```

Observed status codes:

- `Ok` - Request successful
- `ValidationError` - Missing or invalid parameters, sent with HTTP 400
- `ServiceError` - The request could not be served, e.g. `"stop invalid"`, `"no serving lines found"` or `"trip calculation error"`, sent with HTTP 200

Older documentation also lists `InvalidRequest`, `NoData` and `ServerError`, which we have not observed recently.

## Best Practices

1. **Error Handling**: Always check the Status.Code field before processing results
2. **Timeouts**: Set reasonable timeouts (10-30 seconds) for requests
3. **Retries**: Implement exponential backoff for failed requests
4. **Caching**: Cache stop IDs and static data to reduce API calls
5. **User Agent**: Consider setting a descriptive User-Agent header
6. **Rate Limiting**: Be respectful of the service; avoid excessive requests
7. **Format Parameter**: Always include `"format": "json"` in your requests

---

# Sources

- http://data.linz.gv.at/katalog/linz_ag/linz_ag_linien/fahrplan/EFA_XML_Schnittstelle_20151217.pdf
- http://data.linz.gv.at/katalog/linz_ag/linz_ag_linien/fahrplan/LINZ_AG_Linien_Schnitstelle_EFA_v7_Echtzeit.pdf
- http://data.linz.gv.at/katalog/linz_ag/linz_ag_linien/fahrplan/LINZ_LINIEN_Schnittstelle_EFA_V1.pdf
- http://mobilitaet21.de/wp-content/uploads/2016/03/Anlage7-Demonstrator-MDV-EFA_HB_V1.2_201007_EFAFRS.pdf
- https://www.yumpu.com/de/document/read/10943659/efa-version-10-mentz-datenverarbeitung-gmbh
- http://dati.retecivica.bz.it/dataset/575f7455-6447-4626-a474-0f93ff03067b/resource/c4e66cdf-7749-40ad-bcfd-179f18743d84/download/dokumentationxmlschnittstelleapbv32014-08-28.pdf
- DVB mobil Android app v3.1.7
