# VVO Widget API Documentation

Base URL: `http://widgets.vvo-online.de`

## Overview

The Widget API is a simple GET-based interface designed for website integration. Originally created to power embeddable departure monitor widgets, it provides basic transit information in a lightweight JSON format.

**Key Characteristics:**

- Simple GET requests with query parameters
- Lightweight JSON responses (arrays only)
- No authentication required
- Intended for small-scale, non-commercial use
- Covers all VVO network area (not just Dresden)

## Important Usage Restrictions

According to VVO's terms of use:

- **Non-commercial use only** - Commercial usage is explicitly prohibited
- **No excessive automated querying** - The API is intended for interactive use
- **Fair use policy applies** - Be respectful of server resources
- Violation of these terms may result in IP blocking

For commercial applications or high-volume usage, contact VVO directly at opendata@vvo-online.de.

# Abfahrten

Get a list of upcoming departures from a given stop with a few filter options.

### Request

GET `http://widgets.vvo-online.de/abfahrtsmonitor/Abfahrten.do`

Params:

| Name        | Type    | Description                                                      | Required | Default      |
| :---------- | ------- | ---------------------------------------------------------------- | :------- | :----------- |
| `hst`       | String  | Name or ID of the stop                                           | **Yes**  | -            |
| `vz`        | Int     | Time offset in minutes from now (e.g. `5` = 5 minutes in future) | No       | 0            |
| `ort`       | String  | City/municipality name to disambiguate stop (e.g. "Dresden")     | No       | -            |
| `vm`        | String  | Comma-separated list of transport modes to filter                | No       | All modes    |
| `lim`       | Int     | Maximum number of departures to return                           | No       | All          |
| `timestamp` | Int     | Unix timestamp for departure time search                         | No       | Current time |
| `iso`       | Boolean | Return times in ISO format (unconfirmed)                         | No       | false        |

Possible transport modes are listed [here](http://widgets.vvo-online.de/abfahrtsmonitor/Verkehrsmittel.do). Currently included are `AST/Rufbus`, `Rufbus`, `Fähre`, `Regionalbus`, `S-Bahn`, `Seil-/Schwebebahn`, `Stadtbus`, `Straßenbahn`, `Zug`.

### Response

```js
[
  [
    "4", // Line number/identifier
    "Radebeul West", // Direction/destination
    "1", // Minutes until departure
  ],
  ["1", "Prohlis", "2"],
];
```

**Response Format:**

- Outer array contains all departures
- Each departure is an array with exactly 3 elements:
  - Index 0: Line number (String)
  - Index 1: Direction/final destination (String)
  - Index 2: Minutes until departure (String)
- Times are relative (minutes from now), not absolute
- Empty array `[]` returned if no departures found

```
# Example: Next 2 departures from Postplatz in Dresden
curl -X "GET" "http://widgets.vvo-online.de/abfahrtsmonitor/Abfahrten.do?hst=postplatz&ort=Dresden&lim=2"

# Example: Departures 10 minutes from now, only trams and buses
curl -X "GET" "http://widgets.vvo-online.de/abfahrtsmonitor/Abfahrten.do?hst=helmholtzstra%C3%9Fe&ort=Dresden&vz=10&vm=Stra%C3%9Fenbahn,Stadtbus"

# Example: Using stop ID instead of name
curl -X "GET" "http://widgets.vvo-online.de/abfahrtsmonitor/Abfahrten.do?hst=33000037&lim=5"
```

# Haltestelle

Find specific stops given a partial name or search query.

### Request

GET `http://widgets.vvo-online.de/abfahrtsmonitor/Haltestelle.do`

Params:

| Name  | Type   | Description | Required |
| ----- | ------ | ----------- | -------- |
| `ort` | String | City name   | No       |
| `hst` | String | Stop name   | Yes      |

### Response

```js
[
  [
    [
      "Dresden", // City/municipality name
    ],
  ],
  [
    [
      "Helmholtzstraße", // Stop name
      "Dresden", // City where stop is located
      "33000742", // Stop ID (can be used in Abfahrten.do)
    ],
  ],
];
```

**Response Format:**

- Nested array structure with two main sections:
  1. First section: List of matching cities/municipalities
  2. Second section: List of matching stops
- Each stop entry contains: [name, city, stopId]
- Stop IDs can be used directly in departure queries
- Empty sections if no matches found

```
curl -X "GET" "http://widgets.vvo-online.de/abfahrtsmonitor/Haltestelle.do?ort=Dresden&hst=Helmholtz"
```

# Verkehrsmittel (Transport Modes)

Get a list of all available transport modes.

### Request

GET `http://widgets.vvo-online.de/abfahrtsmonitor/Verkehrsmittel.do`

### Response

Returns an array of 2-element arrays. The first element is the internal identifier, the second is the display name used for the `vm` parameter:

```js
[
  ["AST/Rufbus", "Rufbus"], // On-demand bus (AST)
  ["Fähre", "Fähre"], // Ferry
  ["Regionalbus", "Regionalbus"], // Regional bus
  ["Rufbus", "Rufbus"], // On-demand bus
  ["S-Bahn", "S-Bahn"], // Suburban railway
  ["Seil-/Schwebebahn", "Seil-/Schwebebahn"], // Cable car/Funicular
  ["Stadtbus", "Stadtbus"], // City bus
  ["Straßenbahn", "Straßenbahn"], // Tram
  ["Zug", "Zug"], // Train
];
```

Use the second element (display name) in the `vm` parameter of Abfahrten.do to filter departures by transport type.

---

# Integration Examples

## Simple Departure Monitor Widget

```html
<!-- Basic departure monitor for a website -->
<div id="departures"></div>
<script>
  fetch(
    "http://widgets.vvo-online.de/abfahrtsmonitor/Abfahrten.do?hst=postplatz&ort=Dresden&lim=5",
  )
    .then((response) => response.json())
    .then((data) => {
      const html = data
        .map(
          ([line, direction, minutes]) =>
            `<div>${line} → ${direction} in ${minutes} min</div>`,
        )
        .join("");
      document.getElementById("departures").innerHTML = html;
    });
</script>
```

## Home Automation Integration

Many users integrate this API with home automation systems:

- OpenHAB
- Home Assistant
- FHEM
- Custom Raspberry Pi displays

The simple format makes it ideal for IoT devices and embedded systems.

---

# Common Issues and Solutions

1. **Character Encoding**: Stop names may contain German umlauts. Ensure proper UTF-8 handling.

2. **Content-Type**: The API returns `text/html` as Content-Type despite serving JSON. Most JSON parsers handle this fine, but you may need to parse the body explicitly instead of relying on response type detection.

3. **Stop Name Matching**: The API requires exact stop names. Use Haltestelle.do first to find the correct spelling.

4. **No Results**: If you get an empty array, verify:
   - Stop name spelling is exact
   - Add city parameter if stop exists in multiple cities
   - Check if service runs at the requested time
