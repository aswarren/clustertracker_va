
alert("Recalculating!"); //for testing

tsvFile = ""
//tsvFile hardcoded for MVP


const workScript = `  
  importScripts("https://cdnjs.cloudflare.com/ajax/libs/pako/2.0.4/pako_inflate.min.js");
    self.onmessage = async (evt) => {
      const file = evt.data;
      const buf = await file.arrayBuffer();
      const decompressed = pako.inflate(buf);
      self.postMessage(decompressed, [decompressed.buffer]);
    };
  `;
const url = 'https%3A%2F%2Ftaxonium.big-tree.ucsc.edu';

let clusterJSON;
let sampleJSON;
let stateOfInterest = "Virginia"; //hardcoded for MVP
  
async function loadJSON(dataHost, taxoniumURL, file) {
    const workerBlob = new Blob([workScript], {type: 'application/javascript'});
    const workerUrl = URL.createObjectURL(workerBlob);
  
    const worker = new Worker(workerUrl);
  
    const compressedBlob1 = await fetch(dataHost + file + '?v=' + new Date().getTime())
        .then((r) => r.blob());
  
    return new Promise((resolve, reject) => {
        worker.onmessage = ({data}) => {
            const outputFile = JSON.parse(new TextDecoder().decode(data));
            // console.log(outputFile);
            resolve(outputFile);
        };
        worker.onerror = (error) => {
            reject(error);
        };
        worker.postMessage(compressedBlob1);
    });
}

function parseTSV(file)  { //edit later on to deal with surveillance file properly
    const lines = file.trim().split('\n');
    const dataMap = new Map();

    lines.forEach(line => {
        const [key, value] = line.split(/\s+/);
        dataMap.set(String(key), Number(value));
    });

    return dataMap;
}

async function fetchTsvFile() {
    try {
        const response = await fetch('tempData/test_surveillance.tsv');
        const data = await response.text();
        return parseTSV(data);
    } catch (error) {
        console.error('Error fetching the TSV file:', error);
    }
}

function parseLexicon(file)  { //FIX, see below TO-DO
    const lines = file.trim().split('\n');
    const dataMap = new Map();

    lines.forEach(line => {
        const fields= line.split(",");
        dataMap.set(Number(fields[1]), String(fields[2]));
    });

    return dataMap;
}

async function fetchTextFile() { //hardcoded for now, TO-DO: refactor fetch files
    try {
        const response = await fetch('tempData/county_lexicon.va.txt');
        const data = await response.text();
        return parseLexicon(data);
    } catch (error) {
        console.error('Error fetching the TSV file:', error);
    }
}

// Maps region name to ID within regions.js
function createLookupMap(data) {
    var lookupMap = new Map();
    
    data.features.forEach(function(feature) {
        if (feature.properties && feature.properties.name && feature.id) {
            lookupMap.set(feature.properties.name, feature.id);
        }
    });
    
    return lookupMap;
}


async function run() {

    try {
        const clusterJSON = await loadJSON('tempData/', url, 'cluster_data.json.gz');
        const sampleJSON = await loadJSON('tempData/', url, 'sample_data.json.gz');
        const surveillance_table = await fetchTsvFile();
        const lexicon = await fetchTextFile();
        // console.log(surveillance_table);
        // console.log(lexicon);

        iterator = -1;
        for (let cluster of clusterJSON) {
            iterator++;
            if (cluster[1] !== stateOfInterest) {
                continue;
            }
            const currentCluster = sampleJSON[iterator][0];
            const introSample = currentCluster.substring(0, currentCluster.indexOf(',')).toString();
            const fips = surveillance_table.get(introSample);
            // console.log(fips);
            if (fips === undefined) {
                continue;
            }

            const sampleDateArray = cluster[3].split("-");
            let today = new Date();
            today = today.getFullYear()*12 + today.getMonth()+1;
            const sampleDate = sampleDateArray[0]*12 + parseInt(sampleDateArray[1]);
            const monthDiff = today - sampleDate;
            // console.log(today, cluster[3], monthDiff);

            const region = lexicon.get(fips);
            const origin = cluster[7];
            const sampleCount = currentCluster.split(',').length - 1 //Potentially takes up too much memory

            let regionToIDMap = createLookupMap(introData);
            let regionID = regionToIDMap.get(region).toString();
            let originID = regionToIDMap.get(origin).toString();
            let originIndex = parseInt(originID)-1;
            let regionIndex = parseInt(regionID)-1;
            // console.log(sampleDate, region, origin, sampleCount);
            console.log(region, regionToIDMap.get(region));

            let currentOrigin = introData.features[originIndex].properties.intros;
            let currentRegion = introData.features[regionIndex].properties.intros;
            console.log(origin, currentOrigin, currentOrigin[regionID]);
            currentOrigin[regionID] ? currentOrigin[regionID] += sampleCount : currentOrigin[regionID] = sampleCount; //fix
            currentOrigin["raw"+regionID] ? currentOrigin["raw"+regionID] += sampleCount : currentOrigin["raw"+regionID] = sampleCount;
            currentRegion["basecount"] ? currentRegion["basecount"] += sampleCount : currentRegion["basecount"] = sampleCount;

            if (monthDiff <= 12) {
                currentOrigin["12_"+regionID] ? currentOrigin["12_"+regionID] += sampleCount : currentOrigin["12_"+regionID] = sampleCount; //fix
                currentOrigin["12_raw"+regionID] ? currentOrigin["12_raw"+regionID] += sampleCount : currentOrigin["12_raw"+regionID] = sampleCount;
                currentRegion["12_basecount"] ? currentRegion["12_basecount"] += sampleCount : currentRegion["12_basecount"] = sampleCount;
            }
            if (monthDiff <= 6) {
                currentOrigin["6_"+regionID] ? currentOrigin["6_"+regionID] += sampleCount : currentOrigin["6_"+regionID] = sampleCount; //fix
                currentOrigin["6_raw"+regionID] ? currentOrigin["6_raw"+regionID] += sampleCount : currentOrigin["6_raw"+regionID] = sampleCount;
                currentRegion["6_basecount"] ? currentRegion["6_basecount"] += sampleCount : currentRegion["6_basecount"] = sampleCount;
            }
            if (monthDiff <= 3) {
                currentOrigin["3_"+regionID] ? currentOrigin["3_"+regionID] += sampleCount : currentOrigin["3_"+regionID] = sampleCount; //fix
                currentOrigin["3_raw"+regionID] ? currentOrigin["3_raw"+regionID] += sampleCount : currentOrigin["3_raw"+regionID] = sampleCount;
                currentRegion["6_basecount"] ? currentRegion["6_basecount"] += sampleCount : currentRegion["6_basecount"] = sampleCount;
            }
            console.log(origin, currentOrigin, currentOrigin[regionID]);
            // console.log(current);
            


        }
    } catch (error) {
        console.error("Error loading or processing data:", error);
    }
}

// Start the process
run();
