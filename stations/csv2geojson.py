import csv
import json

stations = []

with open('stations.csv') as csv_file:
	reader = csv.reader(csv_file, delimiter=';')
	for row in reader:
		stations.append(row)

# [['Nummer', 'Name mit Ort', 'Name ohne Ort', 'Ort', 'Tarifzone 1 ', 'Tarifzone 2', 'Tarifzone 3', 'WGS84_X', 'WGS84_Y'],
# ['de:14612:1', 'Dresden Bahnhof Mitte', 'Bahnhof Mitte', 'Dresden', '0100', '', '', '13,723395', '51,055642'],

geostations = []
for station in stations[1:]:
	feature = {
		"type": "Feature",
		"properties": {
			"number": station[0],
			"nameWithCity": station[1],
			"name": station[2],
			"city": station[3],
			"tariffZone1": station[4],
			"tariffZone2": station[5],
			"tariffZone3": station[6]
		},
		"geometry": {
			"type": "Point",
			"coordinates": [
				float(station[7].replace(',', '.')),
				float(station[8].replace(',', '.'))
			]
		}
	}
	geostations.append(feature)

geojson = {
	"type": "FeatureCollection",
	"features": geostations
}

with open('stations.json', 'w') as geojson_file:
	geojson_file.write(json.dumps(geojson))