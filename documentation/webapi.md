Base URL: `https://webapi.vvo-online.de`

***All requests take a JSON body to be sent via a POST request. The parameters to be included in this are specified below.***

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

Any info on the format of the strings contained within `Points` would be much appreciated.


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


# TODO

- https://webapi.vvo-online.de/map/pins
- (https://webapi.vvo-online.de/tr/handyticket)
