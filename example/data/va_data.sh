# obtain the VA geojson file for counties
curl 'https://data.virginia.gov/api/geospatial/rgvv-r79s?fourfour=rgvv-r79s&cacheBust=1668025514&date=20240117&accessType=DOWNLOAD&method=export&format=GeoJSON' -o ./va_counties.geojson

#replace VA shape with VA counties
python place_geojson_counties.py  --us us-states.geo.json --state va_counties.geojson --remove Virginia

