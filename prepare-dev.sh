#!/bin/sh

#copy files to production folders
#JS files
cp src/main.js scripts
cp src/csv_to_html_table.js scripts
cp src/jquery.csv.min.js scripts
cp lib/leafletjs/leaflet.js scripts

#CSS files
cp lib/leafletjs/leaflet.css css

echo "Files copied. To run development server type:"
echo "python3 -m http.server"