function updateFilter(startSeconds) {
    const tChoice = parseInt(document.getElementById('tSlider').value, 10);
    filterBy(startSeconds + tChoice * 3600);
}

function filterBy(seconds) {
    let filters = ['==', 'time', seconds];

    for (dataSetConf of conf.dataSets) {
        const mapElement = dataSetConf.isRaw ? map2 : map
        mapElement.setFilter(dataSetConf.name + '-heatRectangles-fareAmounts', filters);
        mapElement.setFilter(dataSetConf.name + '-heatRectangles-tripSpeed', filters);
        mapElement.setFilter(dataSetConf.name + '-values-fareAmounts', filters);
        mapElement.setFilter(dataSetConf.name + '-values-tripSpeed', filters);
        mapElement.setFilter(dataSetConf.name + '-rectangles', filters);
    }
    let date = new Date(seconds * 1000)
    const time = `${date.getHours().toString().padStart(2, "0")}:${date.getMinutes().toString().padStart(2, "0")}`;
    document.getElementById('time').textContent = 'Time: ' + time;
}

function getValuePlottedData() {
    const radioButtons = document.querySelectorAll('input[name="pdRadio"]');
    let valuePlottedData;
    for (const radioButton of radioButtons) {
        if (radioButton.checked) {
            valuePlottedData = radioButton.value;
            break;
        }
    }
    return valuePlottedData
}

function updateDataSet() {
    for (dataSetConf of conf.dataSets) {
        const layerSuffixes = ['heatRectangles-fareAmounts', 'heatRectangles-tripSpeed',
                               'values-fareAmounts', 'values-tripSpeed',
                               'rectangles' ]
        const mapElement = dataSetConf.isRaw ? map2 : map
        layerSuffixes.forEach((layerSuffix) => {
            mapElement.setLayoutProperty(dataSetConf.name + '-' + layerSuffix, 'visibility', 'none')
        });

        const valuePlottedData = getValuePlottedData()
        mapElement.setLayoutProperty(dataSetConf.name + '-heatRectangles-' + valuePlottedData, 'visibility', 'visible');
        mapElement.setLayoutProperty(dataSetConf.name + '-values-' + valuePlottedData, 'visibility', 'visible');

        mapElement.setLayoutProperty(dataSetConf.name + '-rectangles', 'visibility', 'visible');
    }
}

function initializePage(parsed) {
    conf = parsed;
    const startSeconds = conf.startSeconds;
    mapboxgl.accessToken = conf.accessToken;
    map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/outdoors-v11',
        center: [-73.935242, 40.730610],
        zoom: 13
    });
    map2 = new mapboxgl.Map({
        container: 'map2',
        style: 'mapbox://styles/mapbox/outdoors-v11',
        center: [-73.935242, 40.730610],
        zoom: 13
    });
    map2.on('load', function () {
        prepareMap();
        updateFilter(startSeconds);
        updateDataSet();
        document.title = conf.title;
        document
            .getElementById('tSlider')
            .addEventListener('input', function () {
                updateFilter(startSeconds);
            });
        document
            .querySelectorAll('input[name="pdRadio"]')
            .forEach((radioButton) => radioButton.addEventListener('input', function () {
                updateDataSet();
            }));
    });
    const container = '#comparison-container';
    // FIXME swapped because we want anonymous on the right. Rename things and fix this
    new mapboxgl.Compare(map2, map, container, {});

    // This adds the +/- zoom thingy. Adding in both maps, to not have to figure out how to block the slider from
    // running over it.
    map.addControl(new mapboxgl.NavigationControl());
    map2.addControl(new mapboxgl.NavigationControl());
}

function prepareMap() {
    // Assuming that the coarsest comes first here.
    const maxGeoWidth = conf.dataSets[0].geoWidth;
    const minGeoWidth = conf.dataSets[conf.dataSets.length - 1].geoWidth;
    for (dataSetConf of conf.dataSets) {
        if (dataSetConf.isRaw) {
            addDataSet(map2, dataSetConf, minGeoWidth, maxGeoWidth)
        } else {
            addDataSet(map, dataSetConf, minGeoWidth, maxGeoWidth)
        }
    }
}

function addDataSet(mapElement, dataSetConf, minGeoWidth, maxGeoWidth) {
    const geoWidth = parseFloat(dataSetConf.geoWidth);
    const zoomOffset = Math.log2(geoWidth / 0.0001).toFixed(1); // ~2-5
    const minZoomHeatmap = (geoWidth == maxGeoWidth ? 10 : 17.5 - zoomOffset);
    const minZoom = 17.5 - zoomOffset;
    const maxZoom = (geoWidth == minGeoWidth) ? 20 : 17.5 - zoomOffset + 1;
    
    mapElement.addSource(dataSetConf.name + '-polygons', {
        type: 'geojson',
        data: dataSetConf.polygonsFileRelativePath,
        // increase if you see rendering errors
        buffer: 8
    });
    mapElement.addSource(dataSetConf.name + '-centers', {
        type: 'geojson',
        data: dataSetConf.centersFileRelativePath,
        // increase if you see rendering errors
        buffer: 2
    });
    mapElement.addLayer({
        id: dataSetConf.name + '-heatRectangles-fareAmounts',
        type: 'fill',
        source: dataSetConf.name + '-polygons',
        minzoom: minZoomHeatmap,
        maxzoom: maxZoom,
        layout: {
            'visibility': 'none'
        },
        paint: {
            'fill-color': [
                            'interpolate',
                            ['linear'],
                            ['get', 'fare_amounts'],
                            0.0, 'rgba(0,0,255,0)',
                            5.0, 'rgb(65,105,225)',
                            10.0, 'rgb(0,255,255)',
                            20.0, 'rgb(0,255,0)',
                            35.0, 'rgb(255,255,0)',
                            55.0, 'rgb(255,0,0)'
                        ],
            'fill-opacity': [
                'interpolate',
                ['linear'],
                ['zoom'],
                10, 0,
                11, 0.6,
                15.5, 0.6,
                16.5, 0.4
            ],
            'fill-outline-color': 'rgba(255,255,255,0)'
        }
    }, 'waterway-label');
    mapElement.addLayer({
        id: dataSetConf.name + '-values-fareAmounts',
        type: 'symbol',
        source: dataSetConf.name + '-centers',
        minzoom: minZoom,
        maxzoom: maxZoom,
        layout: {
            'visibility': 'none',
            'text-allow-overlap': true,
            'text-ignore-placement': true,
            'text-field': ['to-string', ['get', 'fare_amounts']],
            'text-size': [
                'interpolate',
                ['exponential', 1.99],
                ['zoom'],
                0, 1,
                22, Math.round(1750000 * geoWidth)
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
    mapElement.addLayer({
        id: dataSetConf.name + '-heatRectangles-tripSpeed',
        type: 'fill',
        source: dataSetConf.name + '-polygons',
        minzoom: minZoomHeatmap,
        maxzoom: maxZoom,
        layout: {
            'visibility': 'none'
        },
        paint: {
            'fill-color': [
                            'interpolate',
                            ['linear'],
                            ['get', 'trip_speed'],
                            0.0, 'rgba(0,0,255,0)',
                            10.0, 'rgb(65,105,225)',
                            15.0, 'rgb(0,255,255)',
                            20.0, 'rgb(0,255,0)',
                            30.0, 'rgb(255,255,0)',
                            40.0, 'rgb(255,0,0)'
                        ],
            'fill-opacity': [
                'interpolate',
                ['linear'],
                ['zoom'],
                10, 0,
                11, 0.6,
                15.5, 0.6,
                16.5, 0.4
            ],
            'fill-outline-color': 'rgba(255,255,255,0)'
        }
    }, 'waterway-label');
    mapElement.addLayer({
        id: dataSetConf.name + '-values-tripSpeed',
        type: 'symbol',
        source: dataSetConf.name + '-centers',
        minzoom: minZoom,
        maxzoom: maxZoom,
        layout: {
            'visibility': 'none',
            'text-allow-overlap': true,
            'text-ignore-placement': true,
            'text-field': ['to-string', ['get', 'trip_speed']],
            'text-size': [
                'interpolate',
                ['exponential', 1.99],
                ['zoom'],
                0, 1,
                22, Math.round(1750000 * geoWidth)
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
    mapElement.addLayer({
        id: dataSetConf.name + '-rectangles',
        type: 'fill',
        source: dataSetConf.name + '-polygons',
        minzoom: minZoom,
        maxzoom: maxZoom,
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
