function startAnimation() {
    if (timer !== null) {
        clearInterval(timer);
    }
    document.getElementById('animationButton').textContent = "Stop Animation";
    const timeout = parseInt(document.getElementById('asSlider').value, 10) * 500;
    timer = setInterval(doAnimation, timeout);
}

function stopAnimation() {
    if (timer === null) {
        return;
    }
    clearInterval(timer);
    timer = null;
    document.getElementById('animationButton').textContent = "Start Animation";
}

function updateAnimation() {
    if (timer === null) {
        return;
    }
    startAnimation();
}

function toggleAnimation() {
    if (timer === null) {
        startAnimation();
    } else {
        stopAnimation();
    }
}

function doAnimation() {
    if (!incrementAnimation()) {
        stopAnimation();
    }
}

function incrementAnimation() {
    let tSlider = document.getElementById('tSlider');
    if (parseInt(tSlider.value, 10) < parseInt(tSlider.max, 10)) {
        tSlider.stepUp();
        updateFilter();
        return true;
    } else {
        let dSlider = document.getElementById('dSlider');
        if (parseInt(dSlider.value, 10) < parseInt(dSlider.max, 10)) {
            tSlider.value = tSlider.min;
            dSlider.stepUp();
            updateFilter();
            return true;
        } else {
            return false;
        }
    }
}

function updateFilter() {
    const tChoice = parseInt(document.getElementById('tSlider').value, 10);
    const dChoice = parseInt(document.getElementById('dSlider').value, 10);
    filterBy(startSeconds + dChoice * 86400 + tChoice * 3600);
}

function filterBy(seconds) {
    let filters = ['==', 'time', seconds];
    for (dataSetConf of conf.dataSets) {
        map.setFilter(dataSetConf.name + '-heatmap', filters);
        map.setFilter(dataSetConf.name + '-cloakDataRectangles', filters);
        map.setFilter(dataSetConf.name + '-cloakDataCounts', filters);
    }
    for (dataSetConf of conf.rawDataSets) {
        map2.setFilter(dataSetConf.name + '-heatmap', filters);
        map2.setFilter(dataSetConf.name + '-cloakDataRectangles', filters);
        map2.setFilter(dataSetConf.name + '-cloakDataCounts', filters);
    }
    let date = new Date(seconds * 1000)
    document.getElementById('date').textContent = 'Date: ' + date.toLocaleDateString();
    const time = `${date.getHours().toString().padStart(2, "0")}:${date.getMinutes().toString().padStart(2, "0")}`;
    document.getElementById('time').textContent = 'Time: ' + time;
}

function updateDataSet() {
    const index = parseInt(document.getElementById('dsSlider').value, 10);
    if (currentDataSet !== index) {
        if (0 <= currentDataSet && currentDataSet < conf.dataSets.length) {
            let dataSetConf = conf.dataSets[currentDataSet];
            map.setLayoutProperty(dataSetConf.name + '-heatmap', 'visibility', 'none');
            map.setLayoutProperty(dataSetConf.name + '-cloakDataRectangles', 'visibility', 'none');
            map.setLayoutProperty(dataSetConf.name + '-cloakDataCounts', 'visibility', 'none');
        }
        currentDataSet = index;
        if (conf.dataSets.length - 1 < index) {
            document.getElementById('subtitle').textContent = "No dataset selected";
            document.getElementById('dataSet').textContent = "Dataset: None";
            return;
        }
    }
    dataSetConf = conf.dataSets[index];
    if (document.getElementById('shCheck').checked) {
        map.setLayoutProperty(dataSetConf.name + '-heatmap', 'visibility', 'visible');
    } else {
        map.setLayoutProperty(dataSetConf.name + '-heatmap', 'visibility', 'none');
    }
    if (document.getElementById('srdCheck').checked) {
        map.setLayoutProperty(dataSetConf.name + '-cloakDataRectangles', 'visibility', 'visible');
        map.setLayoutProperty(dataSetConf.name + '-cloakDataCounts', 'visibility', 'visible');
    } else {
        map.setLayoutProperty(dataSetConf.name + '-cloakDataRectangles', 'visibility', 'none');
        map.setLayoutProperty(dataSetConf.name + '-cloakDataCounts', 'visibility', 'none');
    }
    document.getElementById('subtitle').textContent = dataSetConf.subtitle;
    document.getElementById('dataSet').textContent = "Dataset: " + dataSetConf.name;

    // FIXME move
    map2.setLayoutProperty('encounters-raw' + '-heatmap', 'visibility', 'visible');
    map2.setLayoutProperty('encounters-raw' + '-cloakDataRectangles', 'visibility', 'visible');
    map2.setLayoutProperty('encounters-raw' + '-cloakDataCounts', 'visibility', 'visible');
}

function initializePage(parsed) {
    conf = parsed;
    startSeconds = conf.startSeconds;
    mapboxgl.accessToken = conf.accessToken;
    map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/outdoors-v11',
        center: [-73.935242, 40.730610],
        zoom: 13
    });
    map.on('load', function () {
        prepareMap();
        filterBy(startSeconds);
        dsCount = 1 < conf.dataSets.length ? conf.dataSets.length - 1 : 1;
        document.getElementById('dsSlider').max = dsCount;
        if (initialDataSet < 0 || conf.dataSets.length - 1 < initialDataSet) {
            console.log("Only " + conf.dataSets.length + " datasets configured. No dataset with index " +
                initialDataSet + " present. Displaying dataset with index 0.")
            document.getElementById('dsSlider').value = 0;
        } else {
            document.getElementById('dsSlider').value = initialDataSet;
        }
        updateDataSet();
        document.title = conf.title;
        document.getElementById('title').textContent = conf.title;
        document
            .getElementById('dsSlider')
            .addEventListener('input', function () {
                updateDataSet();
            });
        document
            .getElementById('tSlider')
            .addEventListener('input', function () {
                updateFilter();
            });
        document
            .getElementById('dSlider')
            .addEventListener('input', function () {
                updateFilter();
            });
        document
            .getElementById('asSlider')
            .addEventListener('input', function (e) {
                let asChoice = parseInt(e.target.value, 10) - 1;
                if (asChoice === 0) {
                    asChoice = 0.5;
                }
                document.getElementById('animationSpeed').textContent = "Animation step every: " + asChoice + "s"
                updateAnimation();
            });
        document
            .getElementById('animationButton')
            .addEventListener('click', function () {
                toggleAnimation();
            });
        document
            .getElementById('shCheck')
            .addEventListener('change', function (e) {
                updateDataSet();
            });
        document
            .getElementById('srdCheck')
            .addEventListener('change', function (e) {
                updateDataSet();
            });
    });
    map2 = new mapboxgl.Map({
        container: 'map2',
        style: 'mapbox://styles/mapbox/outdoors-v11',
        center: [-73.935242, 40.730610],
        zoom: 13
    });
    map2.on('load', function () {
        prepareMap();
        filterBy(startSeconds);
        dsCount = 1 < conf.dataSets.length ? conf.dataSets.length - 1 : 1;
        document.getElementById('dsSlider').max = dsCount;
        if (initialDataSet < 0 || conf.dataSets.length - 1 < initialDataSet) {
            console.log("Only " + conf.dataSets.length + " datasets configured. No dataset with index " +
                initialDataSet + " present. Displaying dataset with index 0.")
            document.getElementById('dsSlider').value = 0;
        } else {
            document.getElementById('dsSlider').value = initialDataSet;
        }
        updateDataSet();
        document.title = conf.title;
        document.getElementById('title').textContent = conf.title;
        document
            .getElementById('dsSlider')
            .addEventListener('input', function () {
                updateDataSet();
            });
        document
            .getElementById('tSlider')
            .addEventListener('input', function () {
                updateFilter();
            });
        document
            .getElementById('dSlider')
            .addEventListener('input', function () {
                updateFilter();
            });
        document
            .getElementById('asSlider')
            .addEventListener('input', function (e) {
                let asChoice = parseInt(e.target.value, 10) - 1;
                if (asChoice === 0) {
                    asChoice = 0.5;
                }
                document.getElementById('animationSpeed').textContent = "Animation step every: " + asChoice + "s"
                updateAnimation();
            });
        document
            .getElementById('animationButton')
            .addEventListener('click', function () {
                toggleAnimation();
            });
        document
            .getElementById('shCheck')
            .addEventListener('change', function (e) {
                updateDataSet();
            });
        document
            .getElementById('srdCheck')
            .addEventListener('change', function (e) {
                updateDataSet();
            });
    }); 
    const container = '#comparison-container';
    new mapboxgl.Compare(map, map2, container, {
    // Set this to enable comparing two maps by mouse movement:
    // mousemove: true
    });
}

function prepareMap() {
    for (dataSetConf of conf.dataSets) {
        addDataSet(map, dataSetConf)
    }
    for (dataSetConf of conf.rawDataSets) {
        addDataSet(map2, dataSetConf)
    }
}

function addDataSet(mapElement, dataSetConf) {
    const geoWidth = parseFloat(dataSetConf.geoWidth);
    const zoomOffset = Math.log2(geoWidth / 0.0001).toFixed(1);
    mapElement.addSource(dataSetConf.name + '-polygons', {
        type: 'geojson',
        data: dataSetConf.polygonsFileRelativePath
    });
    mapElement.addSource(dataSetConf.name + '-centers', {
        type: 'geojson',
        data: dataSetConf.centersFileRelativePath
    });
    mapElement.addLayer({
        id: dataSetConf.name + '-heatmap',
        type: 'heatmap',
        source: dataSetConf.name + '-centers',
        minzoom: 10,
        layout: {
            'visibility': 'none'
        },
        paint: {
            'heatmap-color': [
                'interpolate',
                ['linear'],
                ['heatmap-density'],
                0, 'rgba(0,0,255,0)',
                0.05, 'rgb(65,105,225)',
                0.35, 'rgb(0,255,255)',
                0.65, 'rgb(0,255,0)',
                0.95, 'rgb(255,255,0)',
                1, 'rgb(255,0,0)'
            ],
            'heatmap-opacity': [
                'interpolate',
                ['linear'],
                ['zoom'],
                10, 0,
                11, 0.6,
                15.5, 0.6,
                16.5, 0.4
            ],
            'heatmap-radius': [
                'interpolate',
                ['exponential', 1.99],
                ['zoom'],
                0, 1,
                22, Math.round(10000000 * geoWidth)
            ],
            'heatmap-weight': ['get', 'encounters'],
            'heatmap-intensity': 0.01
        }
    }, 'waterway-label');
    mapElement.addLayer({
        id: dataSetConf.name + '-cloakDataRectangles',
        type: 'fill',
        source: dataSetConf.name + '-polygons',
        minzoom: Math.max(10, 15 - zoomOffset),
        layout: {
            'visibility': 'none'
        },
        paint: {
            'fill-color': 'rgba(255,255,255,0)',
            'fill-opacity': [
                'interpolate',
                ['linear'],
                ['zoom'],
                15.5 - zoomOffset, 0,
                16 - zoomOffset, 0.1
            ],
            'fill-outline-color': 'rgb(0,0,0)'
        }
    }, 'waterway-label');
    mapElement.addLayer({
        id: dataSetConf.name + '-cloakDataCounts',
        type: 'symbol',
        source: dataSetConf.name + '-centers',
        minzoom: Math.max(10, 16 - zoomOffset),
        layout: {
            'visibility': 'none',
            'text-allow-overlap': true,
            'text-ignore-placement': true,
            'text-field': ['to-string', ['get', 'encounters']],
            'text-size': [
                'interpolate',
                ['exponential', 1.99],
                ['zoom'],
                0, 1,
                22, Math.round(2000000 * geoWidth)
            ]
        },
        paint: {
            'text-opacity': [
                'interpolate',
                ['linear'],
                ['zoom'],
                16.5 - zoomOffset, 0,
                17 - zoomOffset, 0.4,
                21.5 - zoomOffset, 0.4,
                22 - zoomOffset, 0
            ]
        }
    });
}

const urlParams = new URLSearchParams(window.location.search);
const initialDataSet = urlParams.has('ds') ? parseInt(urlParams.get('ds'), 10) : 0;
if (!urlParams.has('conf')) {
    throw new Error("URL parameters do not contain 'conf'!");
}
let map = null
let map2 = null
let conf = null;
let timer = null;
let startSeconds = null;
let currentDataSet = -1;

fetch(urlParams.get('conf'))
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json()
    })
    .then(parsed => initializePage(parsed))
    .catch(error => {
        console.error('There has been a problem fetching the conf file:', error)
    });
