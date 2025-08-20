#!/usr/bin/env python3

# /// script
# dependencies = [
#   "requests<3",
# ]
# ///

import requests
import json
import csv
import sys
from collections import defaultdict

def fetch_vvo_stations():
    """Fetch station data from VVO open data API"""
    url = 'https://www.vvo-online.de/open_data/VVO_STOPS.JSON'
    print(f"Fetching station data from {url}...", file=sys.stderr)

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    print(f"Fetched {len(data)} stations", file=sys.stderr)
    return data

def process_stations(raw_data):
    """Process raw station data into a cleaner format"""
    stations = []

    for stop in raw_data:
        # Extract line information
        lines_by_type = defaultdict(set)
        operators = set()

        for line in stop.get('Lines', []):
            vehicle_type = line.get('Vehicle', 'Unknown')
            line_nr = line.get('LineNr', '')
            operator = line.get('Operator', '')

            if line_nr:
                lines_by_type[vehicle_type].add(line_nr)
            if operator:
                operators.add(operator)

        # Format lines for output
        lines_summary = {}
        for vehicle_type, line_numbers in lines_by_type.items():
            lines_summary[vehicle_type] = sorted(list(line_numbers),
                                               key=lambda x: (not x.isdigit(), x))

        station = {
            'id': stop.get('gid', ''),
            'numeric_id': stop.get('id', ''),
            'name': stop.get('name', ''),
            'city': stop.get('place', ''),
            'name_with_city': f"{stop.get('place', '')} {stop.get('name', '')}".strip(),
            'longitude': float(stop.get('x') or 0),
            'latitude': float(stop.get('y') or 0),
            'operators': sorted(list(operators)),
            'lines': lines_summary,
            'total_lines': sum(len(lines) for lines in lines_summary.values())
        }

        stations.append(station)

    # Sort by city, then name
    stations.sort(key=lambda x: (x['city'], x['name']))
    return stations

def output_json(stations, filename='stations.json'):
    """Output stations as JSON"""
    output = {
        "metadata": {
            "source": "https://www.vvo-online.de/open_data/VVO_STOPS.JSON",
            "count": len(stations),
            "format_version": "2.0"
        },
        "stations": stations
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(stations)} stations to {filename}", file=sys.stderr)

def output_geojson(stations, filename='stations.geojson'):
    """Output stations as GeoJSON"""
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    for station in stations:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [station['longitude'], station['latitude']]
            },
            "properties": {
                "id": station['id'],
                "numeric_id": station['numeric_id'],
                "name": station['name'],
                "city": station['city'],
                "name_with_city": station['name_with_city'],
                "operators": station['operators'],
                "lines": station['lines'],
                "total_lines": station['total_lines']
            }
        }
        geojson['features'].append(feature)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(stations)} stations to {filename}", file=sys.stderr)

def output_csv(stations, filename='stations.csv'):
    """Output stations as CSV"""
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        # Flatten the lines information for CSV
        fieldnames = [
            'id', 'numeric_id', 'name', 'city', 'name_with_city',
            'latitude', 'longitude', 'operators', 'total_lines',
            'tram_lines', 'bus_lines', 'train_lines', 's_bahn_lines'
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for station in stations:
            row = {
                'id': station['id'],
                'numeric_id': station['numeric_id'],
                'name': station['name'],
                'city': station['city'],
                'name_with_city': station['name_with_city'],
                'latitude': station['latitude'],
                'longitude': station['longitude'],
                'operators': '|'.join(station['operators']),
                'total_lines': station['total_lines'],
                'tram_lines': '|'.join(station['lines'].get('Straßenbahn', [])),
                'bus_lines': '|'.join(station['lines'].get('Stadtbus', [])),
                'train_lines': '|'.join(station['lines'].get('Zug', [])),
                's_bahn_lines': '|'.join(station['lines'].get('S-Bahn', []))
            }
            writer.writerow(row)

    print(f"Wrote {len(stations)} stations to {filename}", file=sys.stderr)

def output_markdown_summary(stations, filename='stations_summary.md'):
    """Generate a summary report of the station data"""
    # Collect statistics
    cities = defaultdict(int)
    vehicle_types = defaultdict(int)
    operators_count = defaultdict(int)

    for station in stations:
        cities[station['city']] += 1
        for vehicle_type, lines in station['lines'].items():
            if lines:
                vehicle_types[vehicle_type] += 1
        for operator in station['operators']:
            operators_count[operator] += 1

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# VVO Station Data Summary\n\n")
        f.write(f"Total stations: {len(stations)}\n\n")

        f.write("## Stations by City\n\n")
        for city, count in sorted(cities.items(), key=lambda x: -x[1])[:20]:
            f.write(f"- {city}: {count}\n")
        f.write(f"\n... and {len(cities) - 20} more municipalities\n\n")

        f.write("## Stations by Transit Type\n\n")
        for vtype, count in sorted(vehicle_types.items(), key=lambda x: -x[1]):
            f.write(f"- {vtype}: {count} stations\n")

        f.write("\n## Transit Operators\n\n")
        for operator, count in sorted(operators_count.items(), key=lambda x: -x[1]):
            f.write(f"- {operator}: {count} stations\n")

        # Find major hubs
        f.write("\n## Major Transit Hubs (10+ lines)\n\n")
        hubs = [(s['name_with_city'], s['total_lines']) for s in stations if s['total_lines'] >= 10]
        for hub, lines in sorted(hubs, key=lambda x: -x[1]):
            f.write(f"- {hub}: {lines} lines\n")

    print(f"Wrote summary to {filename}", file=sys.stderr)

def main():
    # Ensure data directory exists
    import os
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Fetch and process data
    raw_data = fetch_vvo_stations()
    stations = process_stations(raw_data)

    # Output in multiple formats to data directory
    output_json(stations, os.path.join(data_dir, 'stations.json'))
    output_geojson(stations, os.path.join(data_dir, 'stations.geojson'))
    output_csv(stations, os.path.join(data_dir, 'stations.csv'))
    output_markdown_summary(stations, os.path.join(data_dir, 'stations_summary.md'))

    print("\nDone! Generated in data/ directory:", file=sys.stderr)
    print("  - stations.json (comprehensive station data)", file=sys.stderr)
    print("  - stations.geojson (GeoJSON format for mapping)", file=sys.stderr)
    print("  - stations.csv (tabular format)", file=sys.stderr)
    print("  - stations_summary.md (statistics and summary)", file=sys.stderr)

if __name__ == "__main__":
    main()
