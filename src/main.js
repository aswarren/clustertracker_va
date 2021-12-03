var map = L.map('mapid', {'tap':false}).setView([36.77, -119.418], 5);
var global_state = "default";
var global_time = "";
var global_state_id = "00";
// var host = "raw.githubusercontent.com/jmcbroome/introduction-website/main/"
var max_basecount = 0;
for (i = 0; i < introData.features.length; i++) {
    let bc = introData.features[i]["properties"]["intros"]["basecount"];
    if (bc > max_basecount) {
        max_basecount = bc;
    }
}

function getColorBase(d) {
    return d > max_basecount * 0.9 ? '#800026' :
           d > max_basecount * 0.75   ? '#BD0026' :
           d > max_basecount * 0.5   ? '#E31A1C' :
           d > max_basecount * 0.25   ? '#FC4E2A' :
           d > max_basecount * 0.1    ? '#FD8D3C' :
           d > max_basecount * 0.05   ? '#FEB24C' :
           d > max_basecount * 0.01    ? '#FED976' :
                      '#FFEDA0';
}

function getColorIntro(d) {
    return d > 1 ? '#800026' :
        d > 0.75  ? '#BD0026' :
        d > 0.5  ? '#E31A1C' :
        d > 0.25  ? '#FC4E2A' :
        d > 0   ? '#FD8D3C' :
        d > -0.25   ? '#FEB24C' :
        d > -0.5   ? '#FED976' :
                    '#FFEDA0';
}

function style(feature) {
    return {
        fillColor: getColorBase(feature.properties.intros[global_time + "basecount"]),
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7
    };
}

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png?{foo}', {foo: 'bar', attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);

var geojson;
geojson = L.geoJson(introData, {
    style: style,
    onEachFeature: onEachFeature
}).addTo(map);

//control to display data for each region on hover
var info = L.control();

info.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
    this.update();
    return this._div;
};

// method to update the info panel control based on feature properties passed
info.update = function (props) {
    deftext = ' - Hover over a county or state';
    if (global_state == "default") {
        // total number of clusters
        str = '<h4># Clusters '
        if (props) {
            countval = props.intros[global_time + "basecount"];
            str += ' in <b>' + props.name + '</b><br />' + countval;
        } else {
            str += deftext;
        }
    } else {
        // number of introductions into region from another region
        str = '<h4># Introductions to ' + global_state 
        if (props) {
            keyval = global_time + "raw" + global_state_id;
            if (keyval in props.intros){
                countval = props.intros[keyval];
            } else {
                countval = 0;
            }
            str += ' from <b>' + props.name + '</b><br />' + countval;
        } else {
            str += deftext;
        }
    }
    // // append time display period
    // if (global_time == '') {
    //     str += '<br />Since start of pandemic';
    // } else if (global_time == '12_') {
    //     str += '<br />Last 12 months';
    // } else if (global_time == '6_') {
    //     str += '<br />Last 6 months';
    // } else if (global_time == '3_') {
    //     str += '<br />Last 3 months';
    // }
    this._div.innerHTML = str;
};

function highlightFeature(e) {
    var layer = e.target;

    layer.setStyle({
        weight: 5,
        color: '#666',
        dashArray: '',
        fillOpacity: 0.7
    });

    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
        layer.bringToFront();
    }
    info.update(layer.feature.properties);
}

function resetHighlight(e) {
    //geojson.resetStyle(e.target);
    e.target.setStyle({
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7
    })
    info.update();
}

function loadTargetTable(target) {
    CsvToHtmlTable.init({
        csv_path: target, 
        element: 'table-container', 
        allow_download: false,
        csv_options: {separator: '\t', delimiter: '\t'},
        datatables_options: {"paging": true, "searching": true, "order": [[9,"desc"]]},
        custom_formatting: [
            [11, function (data,type,row,meta) {
                if (data == "No identifiable samples") {
                    return '<div title="No CDPH sample IDs were found in this cluster.">' + data + "</div>";
                } else {
                    return '<a href="' + encodeURI(data) + '" title="Click to View in CA Big Tree Investigator" target="_blank">View Samples</a>';
                }
              }
            ],[10, function (data,type,row,meta) {
                return '<a href="' + encodeURI(data) + '" title="Click to View in Taxonium" target="_blank">View Cluster</a>';
              }
            ],[9, function (data,type,row,meta) {
                return '<div title="Importance estimate based on cluster size and age. Not directly comparable between regions with varying sequencing levels.">' + data + "</div>"
              }
            ],[8, function (data,type,row,meta) {
                return '<div title="Confidence metric for the origin; 1 is maximal, 0 is minimal.">' + data + "</div>"
              }
            ],[7, function (data,type,row,meta) {
                return '<div title="The origin region with the greatest weight. May not be the true origin, especially if the corresponding confidence value is below 0.5.">' + data + "</div>"
              }
            ],[6, function (data,type,row,meta) {
                return '<div title="Pangolin lineage of the ancestral introduction.">' + data + "</div>"
              }
            ],[5, function (data,type,row,meta) {
                return '<div title="Nextstrain clade of the ancestral introduction.">' + data + "</div>"
              }
            ],[4, function (data,type,row,meta) {
                return '<div title="Date of the latest sample from this cluster.">' + data + "</div>"
              }
            ],[3, function (data,type,row,meta) {
                return '<div title="Date of the earliest sample from this cluster.">' + data + "</div>"
              }
            ],[2, function (data,type,row,meta) {
                return '<div title="Number of samples in this cluster.">' + data + "</div>"
              }
            ],[1, function (data,type,row,meta) {
                return '<div title="Region of this cluster.">' + data + "</div>"
              }
            ],[0, function (data,type,row,meta) {
                return '<div title="The identifier of the internal node inferred to be the ancestral introduction. Can be used with the public protobuf and matUtils.">' + data + "</div>"
              }
            ]
        ]
      });
}

function resetView(e) {
    geojson.eachLayer(function (layer) {
        geojson.resetStyle(layer);
    });
    loadTargetTable('data/display_tables/default_clusters.tsv');
}

function loadStateTable(e) {
    var fname = e.target.feature.properties.name.trim().replace(/\s+/g, '_')
    let path = "data/display_tables/" + fname + "_topclusters.tsv";
    loadTargetTable(path);
}

function changeMap(time) {
    if (time == 0) {
        //reset to default
        global_time = "";
    } else {
        global_time = time + "_";
    }
    if (global_state != "default") {
        geojson.eachLayer(function (layer) {
            if (layer.feature.id == global_state_id) {
                layer.setStyle({fillColor: "#1a0080"});
            } else {
                layer.setStyle({fillColor: getColorIntro(layer.feature.properties.intros[global_time + global_state_id])});
            }
        });
    } else {
        resetView();
    }
}

function zoomToFeature(e) {
    map.fitBounds(e.target.getBounds());
}

function changeView(e) {
    //code to change the displayed heatmaps to the matching intro index
    var clicklayer = e.target;
    if (e.target.options.fillColor == "#1a0080") {
        resetView(e);
        global_state = "default";
        global_state_id = "00";
        legend.update(global_state);
    } else {
        loadStateTable(e);
        global_state = e.target.feature.properties.name;
        global_state_id = e.target.feature.id;
        clicklayer.setStyle({fillColor: "#1a0080"});
        geojson.eachLayer(function (layer, e = clicklayer) {
            if (e.feature.id != layer.feature.id) {
                layer.setStyle({fillColor: getColorIntro(layer.feature.properties.intros[global_time + e.feature.id])})
            }
        });
        legend.update(global_state);
    }
}

var legend = L.control({position: 'bottomleft'});

legend.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info legend'); // create a div with a class "info lengend"
    this.update(global_state);
    return this._div;
};

// method to update the legend control based on feature properties passed
legend.update = function (props) {
    // basic static legend with "high" vs "low" labels
    var ltext = '<i style="background:#800026"></i>high<br>' +
         '<i style="background:#BD0026"></i><br>' +
         '<i style="background:#E31A1C"></i><br>' +
         '<i style="background:#FC4E2A"></i><br>' +
         '<i style="background:#FD8D3C"></i><br>' +
         '<i style="background:#FEB24C"></i><br>' +
         '<i style="background:#FED976"></i><br>' +
         '<i style="background:#FFEDA0"></i>low';
    if (props != "default") {
        ltext = '<strong>Introductions</strong><br><small>Log<sub>10</sub> fold enrichment</small><br>' + 
            ltext + '<br><br><i style="background:#1a0080"></i>Focal Region';
    } else {
        // cut points for creating color bins
        var grades = [1, 0.9, 0.75, 0.5, 0.25, 0.1, 0.05, 0.01];
        ltext = '<strong>Number of Clusters</strong><br>';
        // loop through the bin cut points and generate a label with a colored square for each interval
        for (var i = 0; i < grades.length; i++) {
            const stop = Math.round(max_basecount * grades[i]);
            const start = Math.round(max_basecount * grades[i + 1]);
            ltext += '<i style="background:' + getColorBase(max_basecount * grades[i]) + '"></i> ' +
                (start ?  start + '&ndash;' + stop + '<br>' : '0&ndash;'+ stop);
        }
    }
    this._div.innerHTML = ltext;
}

function onEachFeature(feature, layer) {
    layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
        click: changeView
    });
}

info.addTo(map);
legend.addTo(map);