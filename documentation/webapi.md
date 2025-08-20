# VVO WebAPI Documentation

Base URL: `https://webapi.vvo-online.de`

## Overview

The WebAPI is a JSON-based REST interface used by VVO's mobile web portal (vvo-mobil.de) and the official DVB mobil app. It provides comprehensive access to transit data including stop search, departure monitors, trip planning, and route change information.

**Key Characteristics:**
- All endpoints use POST requests with JSON payloads
- Responses use Microsoft JSON date format: `/Date(timestamp+timezone)/`
- No authentication required for basic queries
- Some endpoints may expect the header `X-Requested-With: de.dvb.dvbmobil`
- Real-time data includes delay information and service alerts

## Technical Notes

### EFA System Background
VVO uses the EFA (Elektronische Fahrplanauskunft) server software from [MENTZ GmbH](https://www.mentz.net/). This system is also used by many other German transit organizations including:
* [NVBW (Nahverkehrsgesellschaft Baden-Württemberg)](https://www.nvbw.de/)
* [Ruhrbahn](https://www.ruhrbahn.de/)
* [DVB](https://www.dvb.de/)
* [VRR (Verkehrsverbund Rhein-Ruhr)](https://www.vrr.de/)
* [Naldo (Verkehrsverbund Neckar-Alb-Donau)](https://www.naldo.de/)
* [VMS (Verkehrsverbund Mittelsachsen)](https://www.vms.de/)
* [KVV (Karlsruher Verkehrsverbund)](https://www.kvv.de/)
* [Verkehrsverbund Steiermark](https://verbundlinie.at/)

### Date Format
All timestamps in responses use Microsoft JSON date format:
- Format: `/Date(milliseconds+timezone)/`
- Example: `/Date(1487778279147+0100)/`
- The timestamp is in milliseconds since Unix epoch
- Timezone offset is included (e.g., +0100 for CET)

### Coordinate System
The API uses GK4 (Gauss-Krüger Zone 4) coordinates for location data. When working with coordinates:
- Right (Rechtswert) and Up (Hochwert) values are used
- These need to be converted for use with standard GPS/WGS84 systems

### Rate Limiting and Stability
Community reports indicate:
- Occasional 503 Service Unavailable errors
- Random timeouts may occur
- IP-based restrictions may apply (e.g., TU Dresden network ranges)
- Implement retry logic with exponential backoff
- Cache responses where appropriate

---

# PointFinder

Find stops based certain parameters.

### Request

POST `https://webapi.vvo-online.de/tr/pointfinder`

JSON body:

| Name        | Type   | Description                     | Required |
| ----------- | ------ | ------------------------------- | -------- |
| `query`     | String | Search query                    | Yes      |
| `limit`     | Int    | Maximum number of results       | No       |
| `stopsOnly` | Bool   | Only search for stops if `true` | No       |
| `regionalOnly` | Bool | Include only stops in VVO area if `true` | No |
| `stopShortcuts` | Bool | Include stop shortcuts if `true` | No |

or

| Name            | Type   | Description                              | Required |
| --------------- | ------ | ---------------------------------------- | -------- |
| `query`         | String | `coord:[right]:[up]` in GK4 coordinates  | Yes      |
| `limit`         | Int    | Maximum number of results                | No       |
| `assignedstops` | Bool   | Include stops assigned to coordinate if `true` | No       |

`[right]` and `[up]` are placeholders for the actual coordinates in this example.

### Response

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
curl -X "POST" "https://webapi.vvo-online.de/tr/pointfinder" \
     -H "Content-Type: application/json; charset=utf-8" \
     -d $'{
  "query": "helmholtz",
  "stopsOnly": true
}'
```

Be aware that the elements of the `Points` array can take different forms with different types. If doing a PointFinder request for a coordinate, the first element will look like the following for example `coord:4621020:504065:NAV4:Nöthnitzer Straße 46|c||Nöthnitzer Straße 46|5655935|4621020|0||`.

Point strings contain nine values separated by a vertical bar (`|`). As far as we know the values are:
| Index | Type | Description | Always included |
| ----- | ---- | ----------- | --------------- |
| 0     | Int or string | ID of a stop (int), or an other type (string, see below) | Yes |
| 1     | String | Unknown. Propably type of point: `a` for streets, `p` for pois, `c` for coordinates | No |
| 2     | String | City name if point is not in the VVO area | No |
| 3     | String | Name of the stop or street | Yes |
| 4     | Int | Right part of the GK4 coordinates | Yes |
| 5     | Int | Up part of the GK4 coordinates | Yes |
| 6     | Int | Distance, when submitting coords in query otherwise 0 | Yes |
| 7     | ??? | Unknown. | No |
| 8     | String | Shortcut of the stop | No |

Instead of a numeric ID for a stop, there are other types of ids:
* streetID
* poiID
* suburbID
* placeID
* coords

### Street IDs

Street IDs contain 17 values separated by colons (`:`). As far as we know the values are:

| Index | Type | Description | Always included |
| ----- | ---- | ----------- | --------------- |
| 0 | String | Suffix for streets: `streetID` | Yes |
| 1 | Int | ID of the street (OMC) | Yes |
| 2 | String | Street number, e.g. for `Musterstraße 42a` it's `42a` | No |
| 3 | Int | Unknown | Yes |
| 4 | Int | Unknown, but mostly `-1` (invalid value) | Yes |
| 5 | String | Street name | Yes |
| 6 | String | City name | Yes |
| 7 | String | Street name | Yes |
| 8 | ??? | Unknown | No |
| 9 | String | Street name | Yes |
| 10 | String | Postal code | Yes |
| 11 | String | `ANY` | Yes |
| 12 | String | Either `DIVA_STREET` for a complete street or `DIVA_SINGLEHOUSE` for a point with street number | Yes |
| 13 | Int | Unknown. Propably right part of coordinates in MDV format | Yes |
| 14 | Int | Unknown. Propably up part of coordinates in MDV format | Yes |
| 15 | String | Map name, e.g. `MRCV` or `NAV4` | Yes |
| 16 | String | Acronym of the transport association, e.g. `VVO` | Yes |

### POI IDs

POI IDs contain 13 values separated by colons (`:`). As far as we know the values are:

| Index | Type | Description | Always included |
| ----- | ---- | ----------- | --------------- |
| 0 | String | Suffix for pois: `poiID` | Yes |
| 1 | Int | ID of the poi | Yes |
| 2 | Int | Unknown. | Yes |
| 3 | Int | Unknown, but mostly `-1` (invalid value) | Yes |
| 4 | String | Name of the poi | Yes |
| 5 | String | City name | Yes |
| 6 | String | Name of the poi | Yes |
| 7 | String | `ANY` | Yes |
| 8 | String | `POI` | Yes |
| 9 | Int | Unknown. Propably right part of coordinates in MDV format | Yes |
| 10 | Int | Unknown. Propably up part of coordinates in MDV format | Yes |
| 11 | String | Map name, e.g. `MRCV` or `NAV4` | Yes |
| 12 | String | Acronym of the transport association, e.g. `VVO` | Yes |

# Departure Monitor

List out upcoming departures from a given stop id.

### Request

POST `https://webapi.vvo-online.de/dm`

JSON body:

| Name               | Type          | Description                              | Required |
| ------------------ | ------------- | ---------------------------------------- | -------- |
| `stopid`           | String        | ID of the stop                           | Yes      |
| `limit`            | Int           | Maximum number of results                | No       |
| `time`             | String        | ISO8601 timestamp, e.g. `2017-02-22T15:40:26Z` | No       |
| `isarrival`        | Bool          | Is the time specified above supposed to be interpreted as arrival or departure time? | No       |
| `shorttermchanges` | Bool          | unknown in this context                  | No       |
| `mot`              | Array[String] | Allowed modes of transport, see below    | No       |

Currently accepted modes of transport are `Tram`, `CityBus`, `IntercityBus`, `SuburbanRailway`, `Train`, `Cableway`, `Ferry`, `HailedSharedTaxi`.

### Response

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
      }
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
      }
    }
  ]
}
```

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
  ]
}'
```


# Trip Details

Get details about the stations involved in a particular trip.

## Request

POST https://webapi.vvo-online.de/dm/trip

### JSON Body:

| Name	    | Type	    | Description	                                                    | Required |
| --------- | --------- | ----------------------------------------------------------------- | -------- |
| `tripid`  | String	| The "id" received from the departure monitor (Departures\[\*\].Id).	| Yes      |
| `time`    | String	| The current time as unix timestamp plus timezone. Has to be in the future. Most likely from a departure monitor response (Departures\[\*\].RealTime / Departures\[\*\].ScheduledTime). | Yes |
| `stopid`  | String	| ID of a stop in the route. This stop will be marked with Position=Current in the response. | Yes |
| `mapdata` | Bool	    | Unknown. Seems to have no effect.	                                | No       |


```
curl -X "POST" "https://webapi.vvo-online.de/dm/trip" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -d $'{
  "tripid": "71313709",
  "time": "/Date(1512563081000+0100)/",
  "stopid": "33000077"
}'
```

## Response
```
{
  "Stops": [
    ...
    {
      "Id": "33000076",
      "Place": "Dresden",
      "Name": "Laibacher Straße",
      "Position": "Previous",
      "Platform": {
        "Name": "2",
        "Type": "Platform"
      },
      "Time": "\/Date(1512563021000+0100)\/"
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
      "Time": "\/Date(1512563081000+0100)\/"
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
    },
    ...
  ],
  "Status": {
    "Code": "Ok"
  },
  "ExpirationTime": "\/Date(1512565171371+0100)\/"
}
```


# Query a Trip

Query how to get from station "Hauptbahnhof" (stopid 33000028) to station
"Bahnhof Neustadt" (stopid 33000016).

## Request

POST https://webapi.vvo-online.de/tr/trips

### JSON body

| Name               | Type        | Description       | Required |
| ------------------ | ----------- | ----------------- | -------- |
| `origin`           | String      | stopid of start station | yes |
| `destination`      | String      | stopid of destination station | yes |
| `shorttermchanges` | Bool        | unknown           | no (missing behaves like `shorttermchanges = false`) |
| `time`             | String      | ISO8601 timestamp | no  |
| `isarrivaltime`    | Bool        | is `time` arrival or departure | no |

```bash
curl -X "POST" "https://webapi.vvo-online.de/tr/trips?format=json" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -H 'X-Requested-With: de.dvb.dvbmobil' \
     -d $'{
            "destination": "33000016",
            "isarrivaltime": false,
            "mobilitySettings": {
                "mobilityRestriction": "None"
            },
            "origin": "33000028",
            "shorttermchanges": true,
            "standardSettings": {
                "footpathToStop": 5,
                "includeAlternativeStops": true,
                "maxChanges": "Unlimited",
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
                "walkingSpeed": "Normal"
            },
            "time": "2017-12-08T21:36:42.775Z"
        }'
```

## Response

```json
{
    "Routes": [
        ...
        {
            "Duration": 11,
            "FareZoneDestination": 10,
            "FareZoneOrigin": 10,
            "Interchanges": 0,
            "MapData": [
                "Tram|5657496|4621684|5657555|4621712|5657572|4621722|5657589|4621733|5657611|4621746|5657637|4621762|5657694|4621796|5657694|4621796|5657700|4621800|5657729|4621819|5657795|4621859|5657861|4621902|5657888|4621922|5657930|4621954|5657978|4621990|5657978|4621990|5658017|4622019|5658176|4622138|5658240|4622191|5658279|4622224|5658347|4622282|5658358|4622291|5658377|4622302|5658414|4622319|5658476|4622350|5658551|4622387|5658551|4622387|5658574|4622398|5658588|4622406|5658595|4622411|5658607|4622421|5658621|4622432|5658628|4622440|5658629|4622441|5658638|4622450|5658661|4622474|5658682|4622494|5658692|4622502|5658702|4622509|5658765|4622541|5658816|4622567|5658852|4622582|5658870|4622587|5658888|4622592|5658901|4622595|5658937|4622602|5658957|4622607|5658957|4622607|5658966|4622609|5658990|4622613|5659010|4622615|5659021|4622615|5659035|4622614|5659058|4622612|5659091|4622606|5659388|4622527|5659435|4622516|5659441|4622514|5659473|4622506|5659512|4622508|5659520|4622508|5659556|4622511|5659556|4622511|5659562|4622512|5659581|4622513|5659603|4622512|5659946|4622487|5659981|4622486|5660008|4622484|5660032|4622487|5660053|4622494|5660065|4622499|5660090|4622515|5660123|4622534|5660124|4622534|5660124|4622534|5660134|4622541|5660148|4622549|5660244|4622401|5660271|4622315|5660278|4622254|5660285|4622217|5660291|4622151|"
            ],
            "MapPdfId": "VVO_5A2B062D3",
            "MotChain": [
                {
                    "Changes": [
                        "510690"
                    ],
                    "Direction": " Btf Trachenberge",
                    "Diva": {
                        "Network": "voe",
                        "Number": "11003"
                    },
                    "Name": "3",
                    "Type": "Tram"
                }
            ],
            "PartialRoutes": [
                {
                    "Duration": 11,
                    "MapDataIndex": 0,
                    "Mot": {
                        "Changes": [
                            "510690"
                        ],
                        "Direction": " Btf Trachenberge",
                        "Diva": {
                            "Network": "voe",
                            "Number": "11003"
                        },
                        "Name": "3",
                        "Type": "Tram"
                    },
                    "PartialRouteId": 0,
                    "RegularStops": [
                        {
                            "ArrivalTime": "/Date(1512769800000-0000)/",
                            "DataId": "33000028",
                            "DepartureTime": "/Date(1512769800000-0000)/",
                            "Latitude": 5657497,
                            "Longitude": 4621685,
                            "MapPdfId": "VVO_5A2B062D4",
                            "Name": "Hauptbahnhof",
                            "Place": "Dresden",
                            "Platform": {
                                "Name": "3",
                                "Type": "Railtrack"
                            },
                            "Type": "Stop"
                        },
                        {
                            "ArrivalTime": "/Date(1512769860000-0000)/",
                            "DataId": "33000032",
                            "DepartureTime": "/Date(1512769860000-0000)/",
                            "Latitude": 5657693,
                            "Longitude": 4621797,
                            "Name": "Hauptbahnhof Nord",
                            "Place": "Dresden",
                            "Platform": {
                                "Name": "1",
                                "Type": "Platform"
                            },
                            "Type": "Stop"
                        },
                        {
                            "ArrivalTime": "/Date(1512769920000-0000)/",
                            "DataId": "33000029",
                            "DepartureTime": "/Date(1512769920000-0000)/",
                            "Latitude": 5657981,
                            "Longitude": 4621985,
                            "Name": "Walpurgisstraße",
                            "Place": "Dresden",
                            "Platform": {
                                "Name": "1",
                                "Type": "Platform"
                            },
                            "Type": "Stop"
                        },
                        {
                            "ArrivalTime": "/Date(1512770040000-0000)/",
                            "DataId": "33000005",
                            "DepartureTime": "/Date(1512770040000-0000)/",
                            "Latitude": 5658549,
                            "Longitude": 4622390,
                            "Name": "Pirnaischer Platz",
                            "Place": "Dresden",
                            "Platform": {
                                "Name": "4",
                                "Type": "Platform"
                            },
                            "Type": "Stop"
                        },
                        {
                            "ArrivalTime": "/Date(1512770100000-0000)/",
                            "DataId": "33000015",
                            "DepartureTime": "/Date(1512770100000-0000)/",
                            "Latitude": 5658956,
                            "Longitude": 4622609,
                            "Name": "Synagoge",
                            "Place": "Dresden",
                            "Platform": {
                                "Name": "2",
                                "Type": "Platform"
                            },
                            "Type": "Stop"
                        },
                        {
                            "ArrivalTime": "/Date(1512770220000-0000)/",
                            "DataId": "33000014",
                            "DepartureTime": "/Date(1512770220000-0000)/",
                            "Latitude": 5659556,
                            "Longitude": 4622513,
                            "Name": "Carolaplatz",
                            "Place": "Dresden",
                            "Platform": {
                                "Name": "4",
                                "Type": "Platform"
                            },
                            "Type": "Stop"
                        },
                        {
                            "ArrivalTime": "/Date(1512770340000-0000)/",
                            "DataId": "33000013",
                            "DepartureTime": "/Date(1512770340000-0000)/",
                            "Latitude": 5660122,
                            "Longitude": 4622537,
                            "Name": "Albertplatz",
                            "Place": "Dresden",
                            "Platform": {
                                "Name": "2",
                                "Type": "Platform"
                            },
                            "Type": "Stop"
                        },
                        {
                            "ArrivalTime": "/Date(1512770460000-0000)/",
                            "DataId": "33000016",
                            "DepartureTime": "/Date(1512770460000-0000)/",
                            "Latitude": 5660290,
                            "Longitude": 4622151,
                            "MapPdfId": "VVO_5A2B062D5",
                            "Name": "Bahnhof Neustadt",
                            "Place": "Dresden",
                            "Platform": {
                                "Name": "2",
                                "Type": "Platform"
                            },
                            "Type": "Stop"
                        }
                    ],
                    "Shift": "None"
                }
            ],
            "Price": "2,30",
            "PriceLevel": 1,
            "RouteId": 1
        },
        ...
    ],
    "SessionId": "367417461:efa4",
    "Status": {
        "Code": "Ok"
    }
}
```


# Route Changes

Get information about route changes because of construction work or such.

## Request

POST https://webapi.vvo-online.de/rc

### JSON body

| Name        | Type        | Description    | Required |
| ----------- | ----------- | -------------- | -------- |
| `shortterm` | Bool        | unknown. I diffed the output with and without -> no diff | no        |

I also tried to pass other keys like mot, name, id, change, ... (each camel, pascal and lower case)
but no error and no change in result. So it looks like you need to fetch all route changes for the
whole VVO and filter yourself.

```bash
curl -X "POST" "https://webapi.vvo-online.de/rc" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -d $'{ "shortterm": true }'
```

## Response

```json
{
    "Changes": [
        ...
        {
            "Description": "<p><DIV ></DIV>\n<H2>Beschreibung</H2>\n<P><STRONG>Buslinie 79:</STRONG><BR>Umleitung <FONT color=#ff0000>nur in Richtung&nbsp;Overbeckstraße</FONT> zwischen den Haltestellen&nbsp;Rethelstraße und&nbsp;Mengsstraße über den Fahrweg <U>Rethelstraße - Werftstraße</U>.</P>\n<H2>Haltestellenanpassungen</H2>\n<UL>\n<LI>Die Haltestellen <STRONG>Kaditzer Straße</STRONG> und <STRONG>Thäterstraße</STRONG>&nbsp;werden in die <U>Rethelstraße</U> verlegt.</LI></UL></p>",
            "Id": "511595",
            "LineIds": [
                "428296"
            ],
            "PublishDate": "/Date(1512400560000+0100)/",
            "Title": "Dresden - Mengsstraße, Vollsperrung wegen Asphaltarbeiten",
            "Type": "Scheduled",
            "ValidityPeriods": [
                {
                    "Begin": "/Date(1512529200000+0100)/",
                    "End": "/Date(1512788400000+0100)/"
                }
            ]
        },
        ...
    ],
    "Status": {
        "Code": "Ok"
    }
}
```

(sometimes they come back: `<font color="#abc" />`)


# Lines

Get information about which lines do service which stations.

## Request

POST https://webapi.vvo-online.de/stt/lines

### JSON body

| Name     | Type   | Description    | Required |
|----------|--------|----------------|----------|
| `stopid` | String | ID of the stop | Yes      |

```bash
curl -X "POST" "https://webapi.vvo-online.de/stt/lines" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -d $'{ "stopid": "33000293" }'
```

## Response

```json
  {
    "Lines": [
      {
        "Name": "41",
        "Mot": "Tram",
        "Changes": [
          "5482",
          "5480",
          "5481"
        ],
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
      },
      {
        "Name": "64",
        "Mot": "CityBus",
        "Changes": [
          "5481",
          "5466",
          "4472"
        ],
        "Directions": [
          {
            "Name": "Dresden Kaditz Am Vorwerksfeld",
            "TimeTables": [
              {
                "Id": "voe:21064: :H:j19:17",
                "Name": "Aktualisierter Standardfahrplan - gültig ab 21.06.2019"
              },
              {
                "Id": "voe:21064: :H:j19:18",
                "Name": "Ferienfahrplan - gültig vom 08.07. bis 18.08.2019"
              }
            ]
          },
          {
            "Name": "Dresden Reick Hülße-Gymnasium",
            "TimeTables": [
              {
                "Id": "voe:21064: :R:j19:17",
                "Name": "Aktualisierter Standardfahrplan - gültig ab 21.06.2019"
              },
              {
                "Id": "voe:21064: :R:j19:18",
                "Name": "Ferienfahrplan - gültig vom 08.07. bis 18.08.2019"
              }
            ]
          }
        ],
        "Diva": {
          "Number": "21064",
          "Network": "voe"
        }
      },
      {
        "Name": "74",
        "Mot": "CityBus",
        "Directions": [
          {
            "Name": "Dresden Marienallee",
            "TimeTables": [
              {
                "Id": "voe:21074:D:H:j19:1",
                "Name": "Standardfahrplan (gültig ab 07.01.2019)"
              }
            ]
          },
          {
            "Name": "Dresden Mathias-Oeder-Straße",
            "TimeTables": [
              {
                "Id": "voe:21074:D:R:j19:1",
                "Name": "Standardfahrplan (gültig ab 07.01.2019)"
              }
            ]
          }
        ],
        "Diva": {
          "Number": "21074D",
          "Network": "voe"
        }
      },
      {
        "Name": "74",
        "Mot": "CityBus",
        "Directions": [
          {
            "Name": "Dresden Marienallee",
            "TimeTables": [
              {
                "Id": "voe:21074: :H:j19:11",
                "Name": "Ferienfahrplan - gültig vom 08.07. bis 18.08.2019"
              }
            ]
          },
          {
            "Name": "Dresden Jägerpark Heideblick",
            "TimeTables": [
              {
                "Id": "voe:21074: :R:j19:11",
                "Name": "Ferienfahrplan - gültig vom 08.07. bis 18.08.2019"
              }
            ]
          }
        ],
        "Diva": {
          "Number": "21074",
          "Network": "voe"
        }
      },
      {
        "Name": "261",
        "Mot": "IntercityBus",
        "Directions": [
          {
            "Name": "Dresden Hauptbahnhof",
            "TimeTables": [
              {
                "Id": "voe:15261:m:H:j19:1",
                "Name": "Jahresfahrplan 2019 - Gültig ab 9. Dezember 2018"
              }
            ]
          },
          {
            "Name": "Sebnitz Busbahnhof",
            "TimeTables": [
              {
                "Id": "voe:15261:m:R:j19:1",
                "Name": "Jahresfahrplan 2019 - Gültig ab 9. Dezember 2018"
              }
            ]
          }
        ],
        "Diva": {
          "Number": "15261m",
          "Network": "voe"
        }
      },
      {
        "Name": "305",
        "Mot": "IntercityBus",
        "Directions": [
          {
            "Name": "Bischofswerda Bahnhof",
            "TimeTables": [
              {
                "Id": "voe:27305: :H:j19:1",
                "Name": "Jahresfahrplan 2019 - Gültig ab 9. Dezember 2018"
              },
              {
                "Id": "voe:27305: :H:j19:4",
                "Name": "Fahrbahnerneuerung S 158 in Rammenau"
              },
              {
                "Id": "voe:27305: :H:j19:6",
                "Name": "Fahrbahnerneuerung S 158 in Rammenau + Fischhausstraße"
              },
              {
                "Id": "voe:27305: :H:j19:7",
                "Name": "Bau Fischhausstraße 29. JUli bis 16. August 2019"
              }
            ]
          },
          {
            "Name": "Dresden Augsburger Straße",
            "TimeTables": [
              {
                "Id": "voe:27305: :R:j19:1",
                "Name": "Jahresfahrplan 2019 - Gültig ab 9. Dezember 2018"
              }
            ]
          },
          {
            "Name": "Dresden Ammonstraße / Budapester Straße",
            "TimeTables": [
              {
                "Id": "voe:27305: :R:j19:4",
                "Name": "Fahrbahnerneuerung S 158 in Rammenau"
              },
              {
                "Id": "voe:27305: :R:j19:6",
                "Name": "Fahrbahnerneuerung S 158 in Rammenau + Fischhausstraße"
              },
              {
                "Id": "voe:27305: :R:j19:7",
                "Name": "Bau Fischhausstraße 29. JUli bis 16. August 2019"
              }
            ]
          }
        ],
        "Diva": {
          "Number": "27305",
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

# Sources
* http://data.linz.gv.at/katalog/linz_ag/linz_ag_linien/fahrplan/EFA_XML_Schnittstelle_20151217.pdf
* http://data.linz.gv.at/katalog/linz_ag/linz_ag_linien/fahrplan/LINZ_AG_Linien_Schnitstelle_EFA_v7_Echtzeit.pdf
* http://data.linz.gv.at/katalog/linz_ag/linz_ag_linien/fahrplan/LINZ_LINIEN_Schnittstelle_EFA_V1.pdf
* http://mobilitaet21.de/wp-content/uploads/2016/03/Anlage7-Demonstrator-MDV-EFA_HB_V1.2_201007_EFAFRS.pdf
* https://www.yumpu.com/de/document/read/10943659/efa-version-10-mentz-datenverarbeitung-gmbh
* http://dati.retecivica.bz.it/dataset/575f7455-6447-4626-a474-0f93ff03067b/resource/c4e66cdf-7749-40ad-bcfd-179f18743d84/download/dokumentationxmlschnittstelleapbv32014-08-28.pdf

# Additional Endpoints (Not Yet Documented)

The following endpoints have been identified but require further documentation:

## Map Pins
- **Endpoint:** `https://webapi.vvo-online.de/map/pins`
- **Purpose:** Likely returns map markers/pins for stops or POIs
- **Method:** POST (assumed)

## Handy Ticket
- **Endpoint:** `https://webapi.vvo-online.de/tr/handyticket`
- **Purpose:** Mobile ticketing integration
- **Method:** POST (assumed)
- **Note:** May require authentication or special access

## POI Search (DVB Maps)
- **Purpose:** Points of Interest search and reverse geocoding
- **Note:** Used by DVB's interactive map at dvb.de/apps/map/
- **Status:** Internal API, not publicly documented

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
