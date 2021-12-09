#!/bin/sh

#copy files to production folders
#JS files
cp src/main.js scripts
cp src/csv_to_html_table.js scripts
cp src/jquery.csv.min.js scripts
cp lib/leafletjs/leaflet.js scripts

#CSS files
cp lib/leafletjs/leaflet.css css

#data files will be hosted on GCloud
#zip and copy Taxonium protobuf
#gzip -k data/cview.pb
#gzip -k data/hardcoded_clusters.tsv
#gsutil cp data/cview.pb.gz gs://ucsc-gi-cdph-bigtree/

echo "Files copied. To deploy to Google App Engine, type:"
echo "gcloud app deploy"
