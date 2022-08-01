// == global variables ==
let grid; // variable for SlickGrid object
let dataView; // data manipulation variable for SlickGrid object
let data = []; //  variable to store data for grid
let basicDataLoaded = false; // basic cluster data are/not loaded into the grid
let sampleDataLoaded = false; // samples are/not loaded into the grid
// web worker script
const workerScript = `  
  importScripts("https://cdnjs.cloudflare.com/ajax/libs/pako/2.0.4/pako_inflate.min.js");
    self.onmessage = async (evt) => {
      const file = evt.data;
      const buf = await file.arrayBuffer();
      const decompressed = pako.inflate(buf);
      self.postMessage(decompressed, [decompressed.buffer]);
    };
  `;
let sortcol = 'growth'; // default column to sort on
let sortdir = -1; // default sort direction
let searchString = ''; // string used to search and sort grid
let regionString = ''; // string to filter grid by region


// == functions for attaching data to grid ==
function blankSampleObj() {
  el = {
    'samples': '',
    'samplecol': '',
    'pauis': '',
    'pauicol': '',
  };
  return el;
}
function blankClusterObj() {
  el = {
    'cid': '...loading data...',
    'region': '',
    'sampcount': '',
    'earliest': '',
    'latest': '',
    'clade': '',
    'lineage': '',
    'origin': '',
    'confidence': '',
    'growth': '',
    'taxlink': '',
    'investigator': '',
  };
  return el;
}
function clusterObjs(items, host) {
  if (items[10] === 0) {
    items[10] = 'No identifiable samples';
  } else {
    items[10] = '<a href="https://investigator.big-tree.ucsc.edu?cid=' + items[0].toString() + '" target="_blank">View ' + items[10].toString() + ' Samples</a>';
  }
  el = {
    'cid': items[0],
    'region': items[1].replace(/_/g, ' '),
    'sampcount': items[2].toString(),
    'earliest': items[3],
    'latest': items[4],
    'clade': items[5],
    'lineage': items[6],
    'origin': items[7].replace(/_/g, ' '),
    'confidence': items[8].toString(),
    'growth': items[9].toString(),
    'taxlink': '<a href="https://taxonium.org/?protoUrl=' + host + 'cview.pb.gz&search=%5B%7B%22id%22:0.123,%22category%22:%22cluster%22,%22value%22:%22' + items[0] + '%22,%22enabled%22:true,%22aa_final%22:%22any%22,%22min_tips%22:1,%22aa_gene%22:%22S%22,%22search_for_ids%22:%22%22%7D%5D&colourBy=%7B%22variable%22:%22region%22,%22gene%22:%22S%22,%22colourLines%22:false,%22residue%22:%22681%22%7D&zoomToSearch=0&blinking=false" target="_blank">View Cluster</a>',
    'investigator': items[10],
  };
  return el;
}
function sampleObjs(items) {
  // full values for searching
  const s = items[0];
  const p = items[1];
  // truncated values for display
  let st = '';
  let pt = '';
  if (s !== '') {
    const n = s.length <= 50 ? s.length - 1 : 50;
    st = s.slice(0, n) + '...';
  }
  if (p !== '') {
    const n = p.length <= 50 ? p.length - 1 : 50;
    pt = p.slice(0, n) + '...';
  }
  el = {
    'samples': s,
    'pauis': p,
    'samplecol': st,
    'pauicol': pt,
  };
  return el;
}
function initData(items, type, host = '') {
  const cl = items.length;
  data = Array(cl);
  if (type === 'clusters') {
    for (let i = 0; i < cl; i++) {
      const d = (data[i] = {});
      d.id = i;
      Object.assign(d, clusterObjs(items[i], host));
      Object.assign(d, blankSampleObj());
    }
  } else if (type === 'samples') {
    for (let i = 0; i < cl; i++) {
      const d = (data[i] = {});
      d.id = i;
      Object.assign(d, blankClusterObj());
      Object.assign(d, sampleObjs(items[i]));
    }
  }
}
function appendData(items, type, host = '') {
  const sl = items.length;
  if (type === 'samples') {
    for (let i = 0; i < sl; i++) {
      const newData = sampleObjs(items[i]);
      data[i].samples = newData.samples;
      data[i].pauis = newData.pauis;
      data[i].samplecol = newData.samplecol;
      data[i].pauicol = newData.pauicol;
    }
  } else if (type === 'clusters') {
    const newData = clusterObjs(items[i], host);
    data[i].cid = newData.cid;
    data[i].region = newData.region;
    data[i].sampcount = newData.sampcount;
    data[i].earliest = newData.earliest;
    data[i].latest = newData.latest;
    data[i].clade= newData.clade;
    data[i].lineage = newData.lineage;
    data[i].origin = newData.origin;
    data[i].confidence = newData.confidence;
    data[i].growth = newData.growth;
    data[i].taxlink = newData.taxlink;
    data[i].investigator = newData.investigator;
  }
}
// function to load the data and wire functions to table
function loadData(dataArr, type, host = '') {
  console.log('end read js, start assigning data to grid variable', Date.now());
  console.log('clusterslenght: ' + dataArr.length);

  if (type === 'clusters') {
    if (!sampleDataLoaded) {
      initData(dataArr, type, host);
    } else if (!basicDataLoaded) {
      // call update function
    }
  } else if (type === 'samples') {
    if (!sampleDataLoaded) {
      initData(dataArr, type);
    } else if (!basicDataLoaded) {
      // call update function
    }
  }

  console.log(data.length);

  setGridView();

  console.log('done loading basic data:', Date.now());
} // end of loadData function
async function loadBasicData(host, file) {
  console.log('loading basic data from: ', host, file, Date.now());
  const workerBlob = new Blob([workerScript], {type: 'application/javascript'});
  const workerUrl = URL.createObjectURL(workerBlob);

  const worker = new Worker(workerUrl);

  // const compressedBlob1 = await fetch(host + 'cluster-data.json.gz?v=' + new Date().getTime())
  const compressedBlob1 = await fetch(host + file + '?v=' + new Date().getTime())
      .then((r) => r.blob());

  worker.onmessage = ({data}) => {
    console.log('success-basic data');
    const clusters = JSON.parse(new TextDecoder().decode(data));

    if (!sampleDataLoaded) {
      loadData(clusters, 'clusters', host);
    } else {
      appendData(clusters, 'clusters', host);
      updateData();
    }

    basicDataLoaded = true;
    console.log('done loading basic data from web worker,', Date.now());
  };
  worker.postMessage(compressedBlob1);
}

async function loadSampleData(host, file) {
  console.log('loading sample data from: ', host, file, Date.now());
  const workerBlob = new Blob([workerScript], {type: 'application/javascript'});
  const workerUrl = URL.createObjectURL(workerBlob);
  const worker = new Worker(workerUrl);

  // const compressedBlob2 = await fetch(host + 'sample-data.json.gz?_=' + new Date().getTime())
  const compressedBlob2 = await fetch(host + file + '?v=' + new Date().getTime())
      .then((r) => r.blob());

  worker.onmessage = ({data}) => {
    console.log('success-sample data');
    const samples = JSON.parse(new TextDecoder().decode(data));
    if (basicDataLoaded) {
      appendData(samples, 'samples');
      updateData();
    } else {
      loadData(samples, 'samples');
    }
    sampleDataLoaded = true;
    console.log('done loading sample data from web worker,', Date.now());
  };
  worker.postMessage(compressedBlob2);
}

// == sets up Slick Grid object properties ==
// slickgrid grid options
function gridOpts() {
  const opt = {
    enableCellNavigation: true,
    forceFitColumns: false,
    multiColumnSort: true,
    enableColumnReorder: false,
  };
  return opt;
}
// sets the number of columns and their parameters
function setCols() {
  const cols = [
    {id: 'cid', name: `<span title='${tooltipText[0]}'>Cluster ID</span>`, field: 'cid', width: 150, sortable: true, sorter: sorterStringCompare, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
    {id: 'region', name: `<span title='${tooltipText[1]}'>Region</span>`, field: 'region', width: 110, sortable: true, sorter: sorterStringCompare, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
    {id: 'sampcount', name: `<span title='${tooltipText[2]}'>Sample Count</span>`, field: 'sampcount', width: 50, sortable: true, sorter: sorterNumeric, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
    {id: 'earliest', name: `<span title='${tooltipText[3]}'>Earliest Date</span>`, field: 'earliest', width: 70, sortable: true, sorter: sorterStringCompare, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
    {id: 'latest', name: `<span title='${tooltipText[4]}'>Latest Date</span>`, field: 'latest', width: 70, sortable: true, sorter: sorterStringCompare, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
    {id: 'clade', name: `<span title='${tooltipText[5]}'>Clade</span>`, field: 'clade', sortable: true, sorter: sorterStringCompare, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
    {id: 'lineage', name: `<span title='${tooltipText[6]}'>Lineage</span>`, field: 'lineage', sortable: true, sorter: sorterStringCompare, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
    {id: 'origin', name: `<span title='${tooltipText[7]}'>Inferred Origin</span>`, field: 'origin', width: 110, sortable: true, sorter: sorterStringCompare, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
    {id: 'confidence', name: `<span title='${tooltipText[8]}'>Inferred Origin Confidence</span>`, field: 'confidence', width: 70, sortable: true, sorter: sorterNumeric, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
    {id: 'growth', name: `<span title='${tooltipText[9]}'>Growth Score</span>`, field: 'growth', width: 70, sortable: true, sorter: sorterNumeric, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
    {id: 'taxlink', name: `<span title='${tooltipText[10]}'>View in Taxonium</span>`, field: 'taxlink', formatter: linkFormatter, sortable: true, sorter: sorterStringCompare},
    {id: 'investigator', name: `<span title='${tooltipText[11]}'>View in Big Tree Investigataor</span>`, field: 'investigator', width: 125, formatter: linkFormatter, sortable: true, sorter: sorterStringCompare},
    {id: 'samplecol', name: `<span title='${tooltipText[12]}'>Samples</span>`, field: 'samplecol', width: 125, sortable: true, sorter: sorterStringCompare, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
    {id: 'pauicol', name: `<span title='${tooltipText[13]}'>Specimen ID/Accession Number</span>`, field: 'pauicol', width: 125, sortable: true, sorter: sorterStringCompare, customTooltip: {useRegularTooltip: true}, formatter: tooltipFormatter},
  ];
  return cols;
}
// initalizes grid with blank data except for first row which shows "loading data"
function tempData() {
  const item = [{id: 'id_0'}];
  Object.assign(item[0], blankClusterObj());
  Object.assign(item[0], blankSampleObj());
  console.log(item)
  return item;
};

// == grid formatting functions ==

// function to add link formatting to cells
function linkFormatter(row, cell, value, columnDef, dataContext) {
  return value;
}
// function to add tool tip text
const tooltipText = [
  'The identifier of the internal node inferred to be the ancestral introduction. Can be used with the public protobuf and matUtils.',
  'Region of this cluster.',
  'Number of samples in this cluster.',
  'Date of the earliest sample from this cluster.',
  'Date of the latest sample from this cluster.',
  'Nextstrain clade of the ancestral introduction.',
  'Pangolin lineage of the ancestral introduction.',
  'The origin region with the greatest weight. May not be the true origin, especially if the corresponding confidence value is below 0.5.',
  'Confidence metric for the origin; 1 is maximal, 0 is minimal.',
  'Importance estimate based on cluster size and age. Not directly comparable between regions with varying sequencing levels.',
  'Click to View in Taxonium',
  'Click to View in California Big Tree Investigator',
  'Double click cell to view all samples in this cluster',
  'Double click cell to view all CDPH Specimen IDs or Accession Numbers for this cluster',
];
function tooltipFormatter(row, cell, value, column, dataContext) {
  let val = '';
  if (value) {
    val = value;
  }

  // set tool tip text to same as header for most non-header cells
  const tttxt = tooltipText[cell];

  return `<span title='${tttxt}'>${val}</span>`;
}

// == grid filtering and sorting ==
// sets which data to search on
function searchFilter(item, args) {
  // show items if no region and no search string
  if (args.searchString === '' && args.regionString === '') {
    return true;
  }
  // filter out items not in the region
  if (args.regionString !== '' && item.region.indexOf(regionString) === -1) {
    return false;
  }
  // make search string case independent
  const sString = args.searchString.toLowerCase();
  // for text searching, fields in the table to search:
  const searchFields = item.cid.toLowerCase().indexOf(sString) === -1 &&
     item.region.toLowerCase().indexOf(sString) === -1 &&
     item.sampcount.toLowerCase().indexOf(sString) === -1 &&
     item.earliest.toLowerCase().indexOf(sString) === -1 &&
     item.latest.toLowerCase().indexOf(sString) === -1 &&
     item.clade.toLowerCase().indexOf(sString) === -1 &&
     item.lineage.toLowerCase().indexOf(sString) === -1 &&
     item.origin.toLowerCase().indexOf(sString) === -1 &&
     item.confidence.toLowerCase().indexOf(sString) === -1 &&
     item.growth.toLowerCase().indexOf(sString) === -1 &&
     item.taxlink.toLowerCase().indexOf(sString) === -1 &&
     item.investigator.toLowerCase().indexOf(sString) === -1 &&
     item.samples.toLowerCase().indexOf(sString) === -1 &&
     item.pauis.toLowerCase().indexOf(sString) === -1;
  // filter out items that don't match search criteria
  if (args.searchString !== '' && searchFields) {
    return false;
  }
  // passes all filters; show item
  return true;
}
function updateFilter() {
  dataView.setFilterArgs({
    regionString,
    searchString,
  });
  dataView.refresh();
}
// function to show/hide data by region
function showRegion(region) {
  if (basicDataLoaded) {
    if (region === 'default') {
      regionString = '';
    } else {
      regionString = region;
    }
    updateFilter();
  } else {
    console.log('basic data not loaded yet');
  }
}
// sort fucntion for strings
function sorterStringCompare(a, b) {
  const x = a[sortcol];
  const y = b[sortcol];
  return sortdir * (x === y ? 0 : (x > y ? 1 : -1));
}
// sort function for numeric data
function sorterNumeric(a, b) {
  const x = (isNaN(a[sortcol]) || a[sortcol] === '' || a[sortcol] === null) ? -99e+10 : parseFloat(a[sortcol]);
  const y = (isNaN(b[sortcol]) || b[sortcol] === '' || b[sortcol] === null) ? -99e+10 : parseFloat(b[sortcol]);
  return sortdir * (x === y ? 0 : (x > y ? 1 : -1));
}


// refreshes grid to show any new data added to data variable
function updateData() {
  dataView.beginUpdate();
  dataView.setItems(data);
  dataView.endUpdate();
  grid.setData(dataView);
  grid.render();

  console.log('done updating data', Date.now());
}

function setGridView() {
  // creates data and grid objects
  dataView = new Slick.Data.DataView({inlineFilters: true});
  grid = new Slick.Grid('#myGrid', dataView, setCols(), gridOpts());


  // adds pagination
  let pager = new Slick.Controls.Pager(dataView, grid, $('#pager'));
  // sets # of items to display by default
  dataView.setPagingOptions({pageSize: 20});

  // set column sort default column; put this before grid.onsort since the data is already sorted
  grid.setSortColumn('growth', false); // columnId, descending sort order


  // adds sorting functionaility
  grid.onSort.subscribe(function(e, args) {
    const cols = args.sortCols;

    dataView.sort(function(dataRow1, dataRow2) {
      const cl = cols.length;
      for (let i = 0; i < cl; i++) {
        sortdir = cols[i].sortAsc ? 1 : -1;
        sortcol = cols[i].sortCol.field;

        const result = cols[i].sortCol.sorter(dataRow1, dataRow2);
        if (result !== 0) {
          return result;
        }
      }
      return 0;
    });
    args.grid.invalidateAllRows();
    args.grid.render();
  });

  // add ability to copy text
  grid.setSelectionModel(new Slick.CellSelectionModel());
  grid.registerPlugin(new Slick.CellExternalCopyManager({
    readOnlyMode: true,
    includeHeaderWhenCopying: false,
  }));

  // wire up model events to drive the grid
  // !! both dataView.onRowCountChanged and dataView.onRowsChanged MUST be wired to correctly update the grid
  // see Issue#91
  dataView.onRowCountChanged.subscribe(function(e, args) {
    grid.updateRowCount();
    grid.render();
  });
  dataView.onRowsChanged.subscribe(function(e, args) {
    grid.invalidateRows(args.rows);
    grid.render();
  });


  // set up double click event to trigger popup
  grid.onDblClick.subscribe((e, p) => {
    // p.row, p.cell
    let txt = '';
    let ttl = '';
    if (p.cell === 12) {
      // get sample names from data
      // txt = grid.getDataItem(p.row).samples;
      txt = data[grid.getDataItem(p.row).id].samples;
      ttl = 'Samples';
    } else if (p.cell === 13) {
      txt = data[grid.getDataItem(p.row).id].pauis;
      ttl = 'Specimen ID/Accession Numbers';
    }
    $('<div id="sample-popup"></div>').dialog({
      title: ttl,
      open: function() {
        txt = txt.replace(/,/g, ',<br/>');
        $(this).html(txt);
        $(this).dblclick(function() {
          $(this).dialog('close');
        });
      },
      height: 300,
    }); // end dialog
  });

  // wire up the search textbox to apply the filter to the model
  $('#txtSearch').keyup(function(e) {
    // clear on Esc
    if (e.which === 27) {
      this.value = '';
    }
    searchString = this.value;
    if (basicDataLoaded && sampleDataLoaded) {
      updateFilter();
    }
  });

  // initialize the model after all the events have been hooked up
  dataView.beginUpdate();
  dataView.setItems(data);
  dataView.setFilterArgs({
    regionString,
    searchString,
  });
  dataView.setFilter(searchFilter);
  dataView.endUpdate();
} // end of setGridView



function initCTGrid(host, clusterfile, samplefile) {
  // clear everything
  basicDataLoaded = false;
  sampleDataLoaded = false;
  data = [];
  sortcol = 'growth';
  sortdir = -1;
  searchString = '';
  regionString = '';
  // create basic grid object while waiting for data to load
  grid = new Slick.Grid('#myGrid', tempData(), setCols(), gridOpts());

  loadBasicData(host, clusterfile);
  loadSampleData(host, samplefile);
}





// (async () => {
//   const workerBlob = new Blob([workerScript], {type: 'application/javascript'});
//   const workerUrl = URL.createObjectURL(workerBlob);

//   const worker1 = new Worker(workerUrl);

//   const compressedBlob1 = await fetch(host + 'cluster-data.json.gz?v=' + new Date().getTime())
//       .then((r) => r.blob());

//   worker1.onmessage = ({data}) => {
//     console.log('success-basic data');
//     const clusters = JSON.parse(new TextDecoder().decode(data));
//     console.log(clusters[21]);
//     loadData(clusters);
//     basicData = true;
//     console.log('done loading basic data from web worker,', Date.now());
//   };
//   worker1.postMessage(compressedBlob1);
// })().catch(console.error);

// (async () => {
//   const workerBlob = new Blob([workerScript], {type: 'application/javascript'});
//   const workerUrl = URL.createObjectURL(workerBlob);
//   const worker2 = new Worker(workerUrl);

//   const compressedBlob2 = await fetch(host + 'sample-data.json.gz?_=' + new Date().getTime())
//       .then((r) => r.blob());

//   worker2.onmessage = ({data}) => {
//     console.log('success-sample data');
//     const samples = JSON.parse(new TextDecoder().decode(data));
//     if (basicData) updateData(samples);
//     console.log('done loading sample data from web worker,', Date.now());
//   };
//   worker2.postMessage(compressedBlob2);
// })().catch(console.error);


// use web worker to load data
// var worker1 = new Worker('load-data-worker.js')
// worker1.addEventListener('message', function(e) {
//   console.log('success-basic data')
//   const clusters = JSON.parse(e.data)
//   //const clusters = e.data
//   console.log(clusters[21])
//   loadData(clusters)
//   basicData = true
//   console.log('done loading basic data from web worker,', Date.now())
// }, false)
// worker1.postMessage('https://storage.googleapis.com/ucsc-gi-cdph-bigtree/display_tables/dev/cluster-data.json') // Send filename to our worker.
// console.log('starting web worker request 2 for sample data,', Date.now())
// var worker2 = new Worker('load-data-worker.js')
// worker2.addEventListener('message', function(e) {
//   console.log('success-sample data')
//   const samples = JSON.parse(e.data)
//   //const samples = e.data
//   if (basicData) updateData(samples)
//   console.log('done loading sample data from web worker,', Date.now())
// }, false)
// worker2.postMessage('https://storage.googleapis.com/ucsc-gi-cdph-bigtree/display_tables/dev/sample-data.json') // Send filename to our worker.


