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


# TODO

- https://webapi.vvo-online.de/tr/trips
- https://webapi.vvo-online.de/map/pins
- https://webapi.vvo-online.de/rc
- https://webapi.vvo-online.de/stt/lines
- (https://webapi.vvo-online.de/tr/handyticket)
