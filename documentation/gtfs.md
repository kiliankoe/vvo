# VVO GTFS Data Documentation

## Overview

VVO/DVB transit data is available through Germany's national GTFS (General Transit Feed Specification) implementation. This provides standardized transit data that can be used with a wide variety of transit applications and services.

## Data Sources

### 1. Germany-wide GTFS Feed (DELFI)

**Static Data URL**: `https://gtfs.de/germany/`

**Key Features:**
- Updated daily
- Covers entire Germany including VVO network
- Includes over 20,000 transit lines
- More than 500,000 stop points
- Nearly 2 million regular vehicle journeys
- Licensed under Creative Commons CC BY-SA 4.0

**Download Options:**
- Complete Germany dataset
- Regional extracts available
- Multiple format options (GTFS, NeTEx)

### 2. GTFS Realtime Feed

**Realtime URL**: `https://gtfs-rt.vvo.de/gtfs-rt-feed`
**Alternative**: `https://realtime.gtfs.de/realtime-free.pb`

**Data Types:**
- Vehicle positions
- Trip updates (delays, cancellations)
- Service alerts
- Stop time updates

**Format**: Protocol Buffers (protobuf)

### 3. VVO Static GTFS Feed

**Official VVO GTFS**: Available through open data portals

**Contents:**
- `agency.txt` - Transit agencies (VVO, DVB)
- `stops.txt` - All stops with coordinates
- `routes.txt` - Transit lines
- `trips.txt` - Individual trips
- `stop_times.txt` - Scheduled arrival/departure times
- `calendar.txt` - Service schedules
- `calendar_dates.txt` - Service exceptions
- `shapes.txt` - Route geometries
- `fare_attributes.txt` - Fare information
- `fare_rules.txt` - Fare zone rules

## Station Data Formats

### CSV Format (from VVO)

VVO publishes a daily updated station list:

**URL**: `https://www.vvo-online.de/open_data/VVO_STOPS.JSON`

**Format Example**:
```csv
stop_id,stop_name,stop_lat,stop_lon,zone_id
de:14612:28,Dresden Hauptbahnhof,51.040142,13.731938,10
de:14612:201,Dresden Hauptbahnhof Nord,51.042806,13.732778,10
```

### GeoJSON Format

The repository includes converted GeoJSON format in `/stations/stations.json`:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [13.731938, 51.040142]
      },
      "properties": {
        "stop_id": "de:14612:28",
        "stop_name": "Dresden Hauptbahnhof",
        "zone_id": 10
      }
    }
  ]
}
```

## Working with GTFS Data

### Using Python

```python
import gtfs_kit as gk
import pandas as pd

# Load GTFS feed
feed = gk.read_feed('vvo_gtfs.zip')

# Get all stops in Dresden
dresden_stops = feed.stops[feed.stops['stop_name'].str.contains('Dresden')]

# Get routes for a specific stop
stop_times = feed.stop_times[feed.stop_times['stop_id'] == 'de:14612:28']
```

### Using Transit.land

VVO data is available through Transit.land API:
- Operator ID: `o-u33-verkehrsverbundoberelbe`
- Coverage: Dresden and surrounding areas

### Using OpenTripPlanner

GTFS data can be loaded into OpenTripPlanner for routing:

```bash
# Download VVO GTFS data
wget https://example.com/vvo-gtfs.zip

# Configure OpenTripPlanner
java -jar otp.jar --build /path/to/data
```

## Legal Framework

### EU Regulation 2017/1926
- Mandates open access to transport data
- Machine-readable formats required
- Free access for non-commercial use
- National Access Points (NAP) required

### German Implementation
- Open Data Directive 2019/1024
- "Open by default" principle
- DELFI as national aggregator
- Datenlizenz Deutschland – Namensnennung 2.0

### License Terms
- **GTFS Data**: CC BY-SA 4.0 or DL-DE-BY 2.0
- **Attribution Required**: "Verkehrsverbund Oberelbe (VVO)"
- **Commercial Use**: May require separate agreement
- **Share-Alike**: Modifications must use same license

## Data Quality Notes

### Update Frequency
- Static data: Daily updates
- Realtime data: Every 10-30 seconds
- Schedule changes: Incorporated within 24 hours

### Known Issues
- Stop IDs may differ between GTFS and API formats
- Coordinate precision varies by data source
- Some rural services may have limited realtime coverage
- Historical data retention varies

## Integration Examples

### Google Maps
VVO GTFS data is integrated into Google Maps:
1. Transit routing available
2. Real-time updates shown
3. Service alerts displayed

### Transit Apps
Compatible with standard transit apps:
- Citymapper
- Transit
- Moovit
- DB Navigator

### Custom Applications
```javascript
// Using GTFS-to-chart
const gtfs = require('gtfs');

gtfs.import({
  agencies: [{
    url: 'https://example.com/vvo-gtfs.zip',
    exclude: []
  }]
}).then(() => {
  console.log('Import completed');
});
```

## Best Practices

1. **Caching**: Cache static GTFS data locally (updates daily)
2. **Filtering**: Extract only needed routes/stops for performance
3. **Validation**: Use GTFS validators before processing
4. **Updates**: Check for feed updates daily
5. **Realtime**: Merge realtime with static data for accuracy

## Tools and Resources

### GTFS Tools
- [GTFS-to-GeoJSON](https://github.com/BlinkTagInc/gtfs-to-geojson)
- [GTFS Validator](https://github.com/google/transitfeed)
- [GTFS Editor](https://github.com/conveyal/gtfs-editor)
- [OpenTripPlanner](https://www.opentripplanner.org/)

### Data Portals
- [GTFS.de](https://gtfs.de/) - German GTFS aggregator
- [MobiData BW](https://www.mobidata-bw.de/) - Regional portal
- [Open Data Sachsen](https://www.opendata.sachsen.de/) - Saxony portal

### Documentation
- [GTFS Reference](https://developers.google.com/transit/gtfs)
- [GTFS Realtime Reference](https://developers.google.com/transit/gtfs-realtime)
- [DELFI Documentation](https://www.delfi.de/)

## Comparison with APIs

| Feature | GTFS | APIs (Widget/WebAPI/TRIAS) |
|---------|------|---------------------------|
| Data freshness | Daily updates + realtime | Real-time |
| Coverage | Entire network | Query-specific |
| Format | CSV/Protocol Buffers | JSON/XML |
| Use case | Bulk data/analysis | Interactive queries |
| Authentication | None | None/API key |
| Rate limits | None (download) | Yes |
