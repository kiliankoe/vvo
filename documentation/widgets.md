Base URL: `http://widgets.vvo-online.de`

# Abfahrten

Get a list of upcoming departures from a given stop with a few filter options.

### Request

GET `http://widgets.vvo-online.de/abfahrtsmonitor/Abfahrten.do`

Params:

| Name        | Type    | Description                              | Required |
| :---------- | ------- | ---------------------------------------- | :------- |
| `hst`       | String  | Name of the stop                         | No       |
| `vz`        | Int     | Time offset, e.g. `1` minute in the future | No       |
| `ort`       | String  | City to further specify the stop         | No       |
| `vm`        | String  | Comma-separated list of allowed transport modes, see below | No       |
| `lim`       | Int     | Maximum number of results                | No       |
| `timestamp` | Int     | Unix timestamp for when to search        | No       |
| `iso`       | unknown | unknown                                  | No       |


Possible transport modes are listed [here](http://widgets.vvo-online.de/abfahrtsmonitor/Verkehrsmittel.do). Currently included are `Rufbus`, `Fähre`, `Regionalbus`, `S-Bahn`, `Seil-/Schwebebahn`, `Stadtbus`, `Straßenbahn`, `Zug`.

### Response

```js
[
  [
    "4", // Line identifier
    "Radebeul West", // Destination
    "1" // Time in minutes until arrival
  ],
  [
    "1",
    "Prohlis",
    "2"
  ]
]
```

```
curl -X "GET" "http://widgets.vvo-online.de/abfahrtsmonitor/Abfahrten.do?hst=postplatz&vz=0&ort=Dresden&lim=2&timestamp=1487172338"
```

# Haltestelle

Find specific stops given a partial name or search query.

### Request

GET `http://widgets.vvo-online.de/abfahrtsmonitor/Haltestelle.do`

Params:

| Name  | Type   | Description | Required |
| ----- | ------ | ----------- | -------- |
| `ort` | String | City name   | No       |
| `hst` | String | Stop name   | No       |

### Response

```js
[
  [
    [
      "Dresden"
    ]
  ],
  [
    [
      "Helmholtzstraße",
      "Dresden",
      "33000742"
    ]
  ]
]
```

```
curl -X "GET" "http://widgets.vvo-online.de/abfahrtsmonitor/Haltestelle.do?ort=Dresden&hst=Helmholtz"
```

# TODO

http://widgets.vvo-online.de/abfahrtsmonitor/Verkehrsmittel.do
