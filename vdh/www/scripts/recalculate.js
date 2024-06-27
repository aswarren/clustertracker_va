
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
            console.log(outputFile);
            resolve(outputFile);
        };
        worker.onerror = (error) => {
            reject(error);
        };
        worker.postMessage(compressedBlob1);
    });
}

function loadTSV(file)  { //edit later on to deal with surveillance file properly
    const lines = file.trim().split('\n');
    const dataMap = new Map();

    lines.forEach(line => {
        const [key, value] = line.split('\t');
        dataMap.set(key, Number(value));
    });

    return dataMap;
}

async function run() {
    try {
        const clusterJSON = await loadJSON('tempData/', url, 'cluster_data.json.gz');
        const sampleJSON = await loadJSON('tempData/', url, 'sample_data.json.gz');
        const surveillance_table = loadTSV(tsvFile);
        console.log(surveillance_table);

        iterator = 0;
        for (let cluster of clusterJSON) {
            if (cluster[1] !== stateOfInterest) {
                continue;
            }
            const currentCluster = sampleJSON[iterator][0];
            const introSample = currentCluster.substring(0, currentCluster.indexOf(','));
            const fips = surveillance_table[introSample];
            // console.log(fips);

            iterator++;
        }

    } catch (error) {
        console.error("Error loading or processing data:", error);
    }
}

// Start the process
run();
