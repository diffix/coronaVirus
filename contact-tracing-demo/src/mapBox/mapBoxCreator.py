import datetime
import http.server
import json
import os.path
import socketserver
import sys
import urllib.parse
from mapBoxConfig import MapBoxConfig
from mapBoxGeoJsonEncoder import MapBoxGeoJsonEncoder


class MapBoxCreator:
    @staticmethod
    def _writeData(name, buckets, latWidth, lonWidth, mapBoxPath):
        dataPath = os.path.join(mapBoxPath, 'data')
        if not os.path.isdir(dataPath):
            os.makedirs(dataPath)
        gjPolygons = MapBoxGeoJsonEncoder.encodeMany(buckets, latWidth, lonWidth, asPoints=False)
        polygonsFileRelativePath = os.path.join('data', f"{name}-polygons.geojson")
        with open(os.path.join(mapBoxPath, polygonsFileRelativePath), 'w') as f:
            json.dump(gjPolygons, f, indent=4)
        gjCenters = MapBoxGeoJsonEncoder.encodeMany(buckets, latWidth, lonWidth, asPoints=True)
        centersFileRelativePath = os.path.join('data', f"{name}-centers.geojson")
        with open(os.path.join(mapBoxPath, centersFileRelativePath), 'w') as f:
            json.dump(gjCenters, f, indent=4)
        return polygonsFileRelativePath, centersFileRelativePath

    @staticmethod
    def _findStartSeconds(buckets):
        minTime = datetime.datetime(year=2100, month=1, day=1, hour=0, minute=0, second=0)
        maxTime = datetime.datetime(year=1970, month=1, day=1, hour=0, minute=0, second=0)
        for bucket in buckets:
            if bucket.time < minTime:
                minTime = bucket.time
            if maxTime < bucket.time:
                maxTime = bucket.time
        minTime = datetime.datetime.combine(minTime.date(), datetime.time(hour=0, minute=0, second=0))
        if datetime.timedelta(days=7) < (maxTime - minTime):
            print(f"Warning, mapbox for more than 7 days requested. Max 7 days supported.")
            print(f"MinTime: {minTime}")
            print(f"MaxTime: {maxTime}")
        return round(minTime.timestamp())

    @staticmethod
    def _createMapLink(title, conf, protocol, host, port, mapboxPath):
        return f"{protocol}://{host}{'' if port is None else f':{port}'}/{mapboxPath}/heatmap.html?" \
               f"title={urllib.parse.quote(title)}&" \
               f"subtitle={urllib.parse.quote(conf['subtitle'])}&" \
               f"startSeconds={conf['startSeconds']}&" \
               f"geoWidth={conf['geoWidth']}&" \
               f"polygonsFilePath={urllib.parse.quote(conf['polygonsFileRelativePath'])}&" \
               f"centersFilePath={urllib.parse.quote(conf['centersFileRelativePath'])}&" \
               f"accessToken={urllib.parse.quote(MapBoxConfig.parameters['accessToken'])}"

    @staticmethod
    def createMap(name, subtitle, buckets, latWidth, lonWidth, mapBoxPath=None):
        if mapBoxPath is None:
            mapBoxPath = os.path.join('www', 'mapbox')
        polygonsFileRelativePath, centersFileRelativePath = MapBoxCreator._writeData(name, buckets, latWidth, lonWidth,
                                                                                     mapBoxPath)
        return {
            'name': name,
            'subtitle': subtitle,
            'polygonsFileRelativePath': polygonsFileRelativePath,
            'centersFileRelativePath': centersFileRelativePath,
            'startSeconds': MapBoxCreator._findStartSeconds(buckets),
            'geoWidth': max(round((latWidth + lonWidth) / 2.0, 6), 0.000001),
        }

    @staticmethod
    def _createMergedMapLinks(conf, protocol, host, port, mapboxPath):
        mainLink = f"{protocol}://{host}{'' if port is None else f':{port}'}/{mapboxPath}/heatmap_conf.html?" \
                   f"conf={conf['confFileRelativePath']}"
        directLinks = list()
        for i in range(len(conf['conf']['dataSets'])):
            directLinks.append((conf['conf']['dataSets'][i]['name'],
                                f"{protocol}://{host}{'' if port is None else f':{port}'}/"
                                f"{mapboxPath}/heatmap_conf.html?conf={conf['confFileRelativePath']}&ds={i}"))
        return mainLink, directLinks

    @staticmethod
    def createMergedMap(name, title, confLst, mapBoxPath=None):
        if mapBoxPath is None:
            mapBoxPath = os.path.join('www', 'mapbox')
        startSeconds = sys.maxsize
        localConfLst = list()
        for conf in confLst:
            if conf['startSeconds'] < startSeconds:
                startSeconds = conf['startSeconds']
            localConf = conf.copy()
            del localConf['startSeconds']
            localConfLst.append(localConf)
        conf = {
            'title': title,
            'accessToken': MapBoxConfig.parameters['accessToken'],
            'startSeconds': startSeconds,
            # FIXME handle moving the raw dataset to rawDataSets
            'dataSets': localConfLst,
        }
        confPath = os.path.join(mapBoxPath, 'conf')
        if not os.path.isdir(confPath):
            os.makedirs(confPath)
        confFileRelativePath = os.path.join('conf', f"{name}.json")
        with open(os.path.join(mapBoxPath, confFileRelativePath), 'w') as f:
            json.dump(conf, f, indent=4)
        return {
            'conf': conf,
            'confFileRelativePath': confFileRelativePath,
        }

    @staticmethod
    def printLinks(name, title, confLst=None, conf=None, protocol="http", host="localhost", port=8000,
                   mapBoxPath="www/mapbox"):
        if confLst is None and conf is None:
            return

        print("--------------------------------------------------")
        print(f"{name} Links")
        if confLst is not None:
            print(f"   Single Map Links:")
            for c in confLst:
                link = MapBoxCreator._createMapLink(title, c, protocol, host, port, mapBoxPath)
                print(f"      {c['name']} ---> {link}")
        if conf is not None:
            print(f"   Merged Map Links:")
            mainLink, directLinks = MapBoxCreator._createMergedMapLinks(conf, protocol, host, port, mapBoxPath)
            print(f"      Direct Links:")
            for n, l in directLinks:
                print(f"         {n} ---> {l}")
            print(f"      Main Link:")
            print(f"         {mainLink}")

    @staticmethod
    def serve():
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", 8000), handler) as httpd:
            print("--------------------------------------------------")
            print(f"Serving http at port 8000")
            httpd.serve_forever()
