# VVO WebAPI Documentation

Base URL: `https://webapi.vvo-online.de`

## Overview

The WebAPI is a JSON-based REST interface used by VVO's mobile web portal (vvo-mobil.de) and the official DVB mobil app. It provides comprehensive access to transit data including stop search, departure monitors, trip planning, route change information, map data, and tariff zone polygons.

**Key Characteristics:**

- Most endpoints use POST requests with JSON payloads (exception: PointFinder uses GET)
- All requests include `"format": "json"` in the payload or query string
- Responses use Microsoft JSON date format: `/Date(timestamp+timezone)/`
- No authentication required for basic queries
- Real-time data includes delay information, occupancy levels, and service alerts

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
- The timestamp is in milliseconds since Unix epoch
- Timezone offset is included (e.g., +0100 for CET)

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

Be aware that the elements of the `Points` array can take different forms with different types. If doing a PointFinder request for a coordinate, the first element will look like the following for example `coord:4621020:504065:NAV4:Nöthnitzer Straße 46|c||Nöthnitzer Straße 46|5655935|4621020|0||`.

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
| 7     | ???           | Unknown                                                           | No              |
| 8     | String        | Shortcut of the stop                                              | No              |

Instead of a numeric ID for a stop, there are other types of ids:

- streetID
- poiID
- suburbID
- placeID
- coords

### Street IDs

Street IDs contain 17 values separated by colons (`:`). As far as we know the values are:

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
| 16    | String | Acronym of the transport association, e.g. `VVO`                                                | Yes             |

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
| `stopid`           | String        | ID of the stop                                    | Yes      |
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
      "Id": "65597047",
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
      "Id": "65598309",
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
| `LineName`      | String        | Line number/name                                           |
| `Direction`     | String        | Destination name                                           |
| `Platform`      | Object        | `Name` (string) and `Type` (`"Platform"` or `"Railtrack"`) |
| `Mot`           | String        | Mode of transport                                          |
| `ScheduledTime` | String        | Planned departure time                                     |
| `RealTime`      | String        | Actual/predicted departure time                            |
| `State`         | String        | Real-time state (e.g. `"Delayed"`, `"InTime"`)             |
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
  "tripid": "71313709",
  "time": "/Date(1512563081000+0100)/",
  "stopid": "33000077",
  "mapdata": true,
  "format": "json"
}'
```

## Response

```json
{
  "Stops": [
    {
      "Id": "33000076",
      "Place": "Dresden",
      "Name": "Laibacher Straße",
      "Position": "Previous",
      "Platform": {
        "Name": "2",
        "Type": "Platform"
      },
      "Time": "\/Date(1512563021000+0100)\/",
      "RealTime": "\/Date(1512563035000+0100)\/",
      "State": "InTime",
      "Latitude": 5654321,
      "Longitude": 4621234,
      "Occupancy": "Unknown"
    },
    {
      "Id": "33000077",
      "Place": "Dresden",
      "Name": "Großglocknerstraße",
      "Position": "Current",
      "Platform": {
        "Name": "2",
        "Type": "Platform"
      },
      "Time": "\/Date(1512563081000+0100)\/",
      "RealTime": "\/Date(1512563095000+0100)\/",
      "State": "InTime",
      "Occupancy": "ManySeats"
    },
    {
      "Id": "33000078",
      "Place": "Dresden",
      "Name": "Friedhof Leuben",
      "Position": "Next",
      "Platform": {
        "Name": "2",
        "Type": "Platform"
      },
      "Time": "\/Date(1512563141000+0100)\/"
    }
  ],
  "MapData": "Tram|5654321|4621234|5654400|4621300|...",
  "Status": {
    "Code": "Ok"
  },
  "ExpirationTime": "\/Date(1512565171371+0100)\/"
}
```

### Stop fields:

| Field           | Type          | Description                                               |
| --------------- | ------------- | --------------------------------------------------------- |
| `Id`            | String        | Stop ID                                                   |
| `Place`         | String        | City name                                                 |
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

The `MapData` field contains pipe-delimited GK4 coordinate pairs for drawing the route on a map, prefixed by the transport mode.

---

# Query a Trip

Plan a journey between two stops.

## Request

POST `https://webapi.vvo-online.de/tr/trips`

### JSON body

| Name               | Type   | Description                           | Required |
| ------------------ | ------ | ------------------------------------- | -------- |
| `origin`           | String | Stop ID of start station              | Yes      |
| `destination`      | String | Stop ID of destination station        | Yes      |
| `time`             | String | ISO8601 timestamp                     | No       |
| `isarrivaltime`    | Bool   | Is `time` arrival or departure        | No       |
| `shorttermchanges` | Bool   | Include short-term route changes      | No       |
| `via`              | String | Stop ID for an intermediate waypoint  | No       |
| `mobilitySettings` | Object | Accessibility preferences (see below) | No       |
| `standardSettings` | Object | Journey preferences (see below)       | No       |
| `format`           | String | Response format, use `"json"`         | No       |

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
  "Routes": [
    {
      "RouteId": 1,
      "Duration": 11,
      "Interchanges": 0,
      "Price": "2,30",
      "PriceLevel": 1,
      "FareZoneOrigin": 10,
      "FareZoneDestination": 10,
      "FareZoneNames": "TZ 10 (Dresden)",
      "NumberOfFareZones": "1",
      "RouteCancelled": false,
      "MapData": ["Tram|5657496|4621684|5657555|4621712|..."],
      "MapPdfId": "VVO_5A2B062D3",
      "MotChain": [
        {
          "Name": "3",
          "Type": "Tram",
          "Direction": " Btf Trachenberge",
          "Changes": ["510690"],
          "Diva": {
            "Network": "voe",
            "Number": "11003"
          }
        }
      ],
      "PartialRoutes": [
        {
          "PartialRouteId": 0,
          "Duration": 11,
          "MapDataIndex": 0,
          "Shift": "None",
          "TripCancelled": false,
          "ChangeoverEndangered": false,
          "BookingLink": "",
          "Infos": [],
          "Mot": {
            "Name": "3",
            "Type": "Tram",
            "Direction": " Btf Trachenberge",
            "Changes": ["510690"],
            "Diva": {
              "Network": "voe",
              "Number": "11003"
            }
          },
          "RegularStops": [
            {
              "DataId": "33000028",
              "Name": "Hauptbahnhof",
              "Place": "Dresden",
              "Type": "Stop",
              "Platform": {
                "Name": "3",
                "Type": "Railtrack"
              },
              "Latitude": 5657497,
              "Longitude": 4621685,
              "ArrivalTime": "/Date(1512769800000-0000)/",
              "DepartureTime": "/Date(1512769800000-0000)/",
              "ArrivalRealTime": "/Date(1512769800000-0000)/",
              "DepartureRealTime": "/Date(1512769800000-0000)/",
              "ArrivalState": "InTime",
              "DepartureState": "InTime",
              "Occupancy": "Unknown",
              "MapPdfId": "VVO_5A2B062D4"
            },
            {
              "DataId": "33000016",
              "Name": "Bahnhof Neustadt",
              "Place": "Dresden",
              "Type": "Stop",
              "Platform": {
                "Name": "2",
                "Type": "Platform"
              },
              "Latitude": 5660290,
              "Longitude": 4622151,
              "ArrivalTime": "/Date(1512770460000-0000)/",
              "DepartureTime": "/Date(1512770460000-0000)/",
              "MapPdfId": "VVO_5A2B062D5"
            }
          ]
        }
      ]
    }
  ],
  "SessionId": "367417461:efa4",
  "Status": {
    "Code": "Ok"
  }
}
```

### Route-level fields:

| Field                 | Type          | Description                                                           |
| --------------------- | ------------- | --------------------------------------------------------------------- |
| `RouteId`             | Int           | Route identifier                                                      |
| `Duration`            | Int           | Total duration in minutes                                             |
| `Interchanges`        | Int           | Number of transfers                                                   |
| `Price`               | String        | Price as string (e.g. `"2,30"` or `"350"` in cents)                   |
| `PriceLevel`          | Int           | Price level                                                           |
| `FareZoneOrigin`      | Int           | Origin fare zone number                                               |
| `FareZoneDestination` | Int           | Destination fare zone number                                          |
| `FareZoneNames`       | String        | Human-readable zone names, e.g. `"TZ 10 (Dresden), TZ 23 (Radebeul)"` |
| `NumberOfFareZones`   | String        | Number of fare zones traversed                                        |
| `RouteCancelled`      | Bool          | Whether the entire route is cancelled                                 |
| `MapData`             | Array[String] | Pipe-delimited GK4 coordinate strings, prefixed with transport mode   |
| `MotChain`            | Array[Object] | Summary of transport modes used                                       |
| `PartialRoutes`       | Array[Object] | Individual legs of the journey                                        |
| `SessionId`           | String        | Session ID for pagination (use with tr/prevnext)                      |

### PartialRoute fields:

| Field                  | Type          | Description                                     |
| ---------------------- | ------------- | ----------------------------------------------- |
| `PartialRouteId`       | Int           | Leg identifier                                  |
| `Duration`             | Int           | Leg duration in minutes                         |
| `MapDataIndex`         | Int           | Index into the route's MapData array            |
| `Shift`                | String        | Shift indicator                                 |
| `TripCancelled`        | Bool          | Whether this specific leg is cancelled          |
| `ChangeoverEndangered` | Bool          | Whether the transfer to the next leg is at risk |
| `BookingLink`          | String        | Service hotline URL (for on-demand services)    |
| `Infos`                | Array[String] | Additional information                          |
| `Mot`                  | Object        | Transport mode details for this leg             |

### RegularStop fields:

| Field               | Type   | Description                                               |
| ------------------- | ------ | --------------------------------------------------------- |
| `DataId`            | String | Stop ID                                                   |
| `Name`              | String | Stop name                                                 |
| `Place`             | String | City name                                                 |
| `Type`              | String | `"Stop"`                                                  |
| `Platform`          | Object | `Name` and `Type` (`"Platform"` or `"Railtrack"`)         |
| `Latitude`          | Int    | GK4 latitude                                              |
| `Longitude`         | Int    | GK4 longitude                                             |
| `ArrivalTime`       | String | Scheduled arrival                                         |
| `DepartureTime`     | String | Scheduled departure                                       |
| `ArrivalRealTime`   | String | Actual/predicted arrival (if real-time data available)    |
| `DepartureRealTime` | String | Actual/predicted departure (if real-time data available)  |
| `ArrivalState`      | String | Real-time state for arrival                               |
| `DepartureState`    | String | Real-time state for departure                             |
| `Occupancy`         | String | `"Unknown"`, `"ManySeats"`, `"StandingOnly"`, or `"Full"` |

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

Same structure as [tr/trips](#query-a-trip) response, including a new `SessionId` for continued pagination.

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

Same structure as [tr/trips](#query-a-trip) response.

---

# Trip PDF Export

Generate a PDF document for a planned trip.

## Request

GET `https://webapi.vvo-online.de/tr/trippdf`

All parameters are passed as query string parameters.

| Name               | Type   | Description                       | Required |
| ------------------ | ------ | --------------------------------- | -------- |
| `id`               | String | Trip/route ID                     | Yes      |
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
      "Id": "511595",
      "Title": "Dresden - Mengsstraße, Vollsperrung wegen Asphaltarbeiten",
      "Description": "<p>...</p>",
      "Type": "Scheduled",
      "TripRequestInclude": true,
      "PublishDate": "/Date(1512400560000+0100)/",
      "LineIds": ["428296"],
      "ValidityPeriods": [
        {
          "Begin": "/Date(1512529200000+0100)/",
          "End": "/Date(1512788400000+0100)/"
        }
      ]
    }
  ],
  "Banners": [
    {
      "Title": "Important notice",
      "Description": "<p>...</p>",
      "Type": "MobileWebsite",
      "ModifiedTime": "/Date(1512400560000+0100)/",
      "TripRequestInclude": false
    }
  ],
  "Lines": [
    {
      "Id": "428296",
      "Name": "79",
      "Mot": "CityBus",
      "TransportationCompany": "DVB"
    }
  ],
  "Status": {
    "Code": "Ok"
  }
}
```

### Change fields:

| Field                | Type          | Description                                             |
| -------------------- | ------------- | ------------------------------------------------------- |
| `Id`                 | String        | Disruption ID                                           |
| `Title`              | String        | Short description                                       |
| `Description`        | String        | HTML-formatted detailed description                     |
| `Type`               | String        | `"Scheduled"` (planned construction) or disruption type |
| `TripRequestInclude` | Bool          | Whether this affects trip planning results              |
| `PublishDate`        | String        | When the change was published                           |
| `LineIds`            | Array[String] | Affected line IDs                                       |
| `ValidityPeriods`    | Array[Object] | Each with `Begin` and `End` timestamps                  |

The response also includes `Banners` (general announcements, filter by `Type: "MobileWebsite"`) and `Lines` (metadata for all affected lines including `Id`, `Name`, `Mot`, and `TransportationCompany`).

Note: HTML in `Description` may include inline styles like `<font color="#abc" />`.

---

# Route Change Lines

Get a list of all lines that have active route changes.

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
      "Id": "428296",
      "Name": "79",
      "Mot": "CityBus",
      "TransportationCompany": "DVB",
      "Divas": [{ "Number": "21079" }]
    }
  ],
  "Status": {
    "Code": "Ok"
  }
}
```

---

# Lines

Get information about which lines service a station.

## Request

POST `https://webapi.vvo-online.de/stt/lines`

### JSON body

| Name     | Type   | Description                   | Required |
| -------- | ------ | ----------------------------- | -------- |
| `stopid` | String | ID of the stop                | Yes      |
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

---

# Map Pins

Get map markers/pins for stops, POIs, and other points of interest within a bounding box.

## Request

POST `https://webapi.vvo-online.de/map/pins`

### JSON body

| Name       | Type          | Description                   | Required |
| ---------- | ------------- | ----------------------------- | -------- |
| `swlat`    | String        | Southwest latitude (GK4)      | Yes      |
| `swlng`    | String        | Southwest longitude (GK4)     | Yes      |
| `nelat`    | String        | Northeast latitude (GK4)      | Yes      |
| `nelng`    | String        | Northeast longitude (GK4)     | Yes      |
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
    "33000028||Dresden|Hauptbahnhof|5657497|4621685|",
    "pf:1234||Dresden|Hauptbahnhof Gleis 3|5657500|4621690|3",
    "pr:5678||Dresden|P+R Hauptbahnhof|5657400|4621600|"
  ],
  "Status": {
    "Code": "Ok"
  }
}
```

Pin strings are pipe-delimited with the same format as [PointFinder](#pointfinder) results. The ID prefix indicates the type:

| Prefix    | Type             |
| --------- | ---------------- |
| (numeric) | Stop             |
| `pf:`     | Platform         |
| `pr:`     | Park and Ride    |
| `p:`      | POI              |
| `r:`      | Rent a Bike      |
| `t:`      | Ticket Machine   |
| `c:`      | Car Sharing      |
| `w:`      | Walking/footpath |

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
  "Polygons": [
    "10|Dresden|#FF0000|5657000|4621000|5657100|4621100|5657200|4621200|..."
  ],
  "ExpirationTime": "\/Date(1512565171371+0100)\/"
}
```

Polygon strings are pipe-delimited:

| Index | Description                                                                 |
| ----- | --------------------------------------------------------------------------- |
| 0     | Zone number                                                                 |
| 1     | Zone name                                                                   |
| 2     | Display color (hex)                                                         |
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

Common status codes:

- `Ok` - Request successful
- `InvalidRequest` - Malformed request or missing parameters
- `NoData` - No results found
- `ServerError` - Internal server error

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
