# Dresden Open Data Portal - Public Transit Datasets

Dresden provides comprehensive Open Data datasets through the municipal geodata portal. This documentation provides an overview of available public transit-related datasets and demonstrates how to access them.

## Accessing the Data

### OGC API Features (OAF)
The datasets are available through a standardized OGC API Features interface.

**Base URL:**
```
https://kommisdd.dresden.de/net4/public/ogcapi/collections/{LAYER_ID}/items
```

### Available Formats
- **GeoJSON**: Geographic data in GeoJSON format (default)
- **JSON**: Structured data without geometry conversion

### Query Parameters
- `limit`: Number of returned records (default: 10, maximum: varies)
- `offset`: For pagination of larger datasets
- Additional OGC-compliant filters depending on dataset

### Coordinate System
- **EPSG:4326** (WGS84) for GeoJSON output
- **EPSG:25833** (ETRS89 / UTM zone 33N) for internal storage

## Overview of Available Public Transit Datasets

### 🚊 DVB-specific Datasets

#### DVB Service Points (L1087)
- **Description**: Locations of DVB customer service points and service locations
- **Format**: Point (GeoJSON)
- **Attributes**: `art` (type), `name0` (name), `url` (website)

### 🚋 Tram Datasets

#### Infrastructure
- **Tram Tracks** (L124)
  - Route of tram rails
  - Geometry: MultiLineString

- **Traffic, Tram Tracks** (L80)
  - Detailed cartographic representation
  - Additional infrastructure information

- **Bridges over Tram Tracks** (L76)
  - Overpasses over tram rails

- **Bridges under Tram Tracks** (L77)
  - Underpasses under tram rails

#### Line Routes
- **Tram Lines** (L457)
  - **Main dataset** with all tram lines
  - **Attributes**:
    - `slinie`: Line number
    - `anfang`/`ende`: Start and end stops
    - `takt`: Service frequency in minutes
    - `verkehrsmittel`: Transport mode type (STRABA)
    - `url_linienaenderung`: Link to current changes
  - **Geometry**: MultiLineString (line route)

- **Individual Lines** (L457..1 to L457..12)
  - Separate layers for each tram line (1-13)
  - Identical structure to main dataset

#### Environmental Data
- **Tram Noise Index L_Night** (L1511)
  - Nighttime noise levels from trams
  - Raster format with dB(A) values

- **Tram Noise Index L_DEN** (L1518)
  - Day-evening-night noise index
  - EU-compliant noise mapping

### 🚌 Bus Datasets

#### Line Routes
- **Bus Lines** (L1076)
  - **Main dataset** with all bus lines
  - **Attributes**:
    - `buslinie`: Line number
    - `anfang`/`ende`: Start and end stops
    - `takt`: Service frequency (1=infrequent, 2=frequent)
    - `verkehrsmittel`: Type (SBUS, etc.)
  - **Geometry**: LineString or MultiLineString

- **Individual Bus Lines** (L1076..1 to L1076..47)
  - Separate layers for lines 61-424 and special lines
  - Also includes Alita on-demand taxis (95, 97)
  - Regional buses (98A-C, 160, 226-261, 333-424)

#### Infrastructure
- **Tour Bus Parking** (L738)
  - Locations for tour buses
  - Point geometry with capacity information

### 🚏 Stop Datasets

#### Stops with Accessibility Information (L1233)
- **Most comprehensive stop dataset**
- **Important Attributes**:
  - `hst_name`: Stop name
  - `steig`: Platform number
  - `verkehrende_linien`: Serving lines
  - `verkehrsmittel`: Transport mode type
  - `globale_id`: VVO stop identifier
- **Accessibility Attributes**:
  - `best_einstieg`: Boarding accessibility rating (10-40)
  - `bordhoehe`: Curb height in cm
  - `breite`: Waiting area width in m
  - `ls_txt`: Tactile paving strips present
  - `afs_txt`: Tactile guidance strips present
- **Coordinates**: Point (WGS84)

### 🗺️ Additional Transport-related Datasets

#### Traffic Noise
- Rail traffic noise (L796, L797, L914, L911)
- Road traffic noise (L795, L798, L912, L913)

#### Transport Infrastructure
- Public roads (L592, L1264)
- Ferries and landing stages (L81)
- Bridges and tunnels (L79, L48)

#### Accessibility
- Accessibility info portal - Transport (L1171)
- Accessible entrances (L1172)

---

## Code Examples

### Python Example: Fetching Tram Lines

```python
import requests
import json

# Fetch all tram lines
url = "https://kommisdd.dresden.de/net4/public/ogcapi/collections/L457/items"
params = {
    "limit": 50  # Fetch all lines
}

response = requests.get(url, params=params)
data = response.json()

# Output lines sorted by number
for feature in data["features"]:
    props = feature["properties"]
    print(f"Line {props['slinie']}: {props['anfang']} - {props['ende']}")
    print(f"  Frequency: {props['takt']} minutes ({props['takt_bemerkung']})")
    print(f"  Changes: {props['url_linienaenderung']}")
    print()
```

### JavaScript Example: Finding Accessible Stops

```javascript
// Search for stops with good accessibility
const url = 'https://kommisdd.dresden.de/net4/public/ogcapi/collections/L1233/items';
const params = new URLSearchParams({ limit: 100 });

fetch(`${url}?${params}`)
  .then(response => response.json())
  .then(data => {
    // Only stops with good accessible boarding (value 10)
    const accessible = data.features.filter(
      f => f.properties.best_einstieg === 10
    );

    console.log(`${accessible.length} accessible stops found`);

    accessible.forEach(stop => {
      const p = stop.properties;
      console.log(`${p.hst_name} (Platform ${p.steig})`);
      console.log(`  Lines: ${p.verkehrende_linien}`);
      console.log(`  Curb height: ${p.bordhoehe} cm`);
    });
  });
```

### curl Example: Filter Bus Lines by Frequency

```bash
# Fetch all frequently running bus lines (takt=2)
curl -X GET \
  "https://kommisdd.dresden.de/net4/public/ogcapi/collections/L1076/items?limit=100" \
  | jq '.features[] | select(.properties.takt == 2) |
         {line: .properties.buslinie,
          route: (.properties.anfang + " - " + .properties.ende)}'
```

### Using with QGIS

1. **Add Layer**: Layer → Add Layer → WFS Layer
2. **Enter URL**: `https://kommisdd.dresden.de/net4/public/ogcapi/collections/`
3. **Select Layer**: e.g., L457 for tram lines
4. **Adjust Style**: Color by line number

---

## Notes and Limitations

### Data Currency
- Line routes are updated regularly
- Construction-related changes not always included

### Performance
- Large datasets should be paginated using `limit` and `offset`
- GeoJSON format can become large with complex geometries
- Observe cache headers for efficient usage

### License
- Open Data License of the City of Dresden
- Attribution required: "Landeshauptstadt Dresden"
- Commercial use permitted

---

## Additional Resources

### Official Documentation
- [Dresden Open Data Portal](https://opendata.dresden.de/)
- [OGC API Features Specification](https://ogcapi.ogc.org/features/)

### Tools and Libraries
- [dresden-opendata-mcp](https://github.com/kiliankoe/dresden-opendata-mcp) - MCP Tool for Dresden Open Data
- [QGIS](https://qgis.org/) - Open Source GIS for geodata visualization
