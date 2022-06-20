from mapBoxCloakAccess import MapBoxCloakAccess
from mapBoxCreator import MapBoxCreator


"""
Create Heatmap from Cloak data
------------------------------

This script queries aircloak for bucketized encounter data and creates a local web page to view the data on a map.
The map shows a heat map of encounters, with exact data once one zooms in.
The map features sliders to dynamically switch between days and hours. By default the sliders support 7 days with
24 hours each. The sliders are not adjustable. When there is less data, there will just be no data shown for some
slider positions. When there is more data, data beyond 7 days from the first occurring date will not be shown.

HowTo:
Make sure you have configured files cloakConfig.py and mapBoxConfig.py in the conf folder. There are example files
to help you. You can configure Aircloak App Logins at https://covid-db.aircloak.com/app_logins and find your
tokens for mapbox at https://account.mapbox.com/access-tokens/. Your mapbox token must be a public token, secret tokens
won't work. Your default public token is a good choice.

The conf folder needs to be on your PYTHONPATH together with all src folders (src, dataAccess, sqlAccess, mapBox).
The current example configuration for the cloak configures a cache of SQL results on disk in a cache folder.
The script was always called from the repository's base folder (where this file is located).

The script requests data from the cloak for two differently sized sets of buckets. For each set it creates GeoJSON files
in the www/mapbox/data folder. It further prints a clickable Link to a local http server. The link only works, once all
data processing has finished and the script announces that it is now serving http on port 8000. All links are printed
in two different versions. Whether and which version is clickable depends on your console/terminal.

The script must continue to run until all http interactions have finished. It will not finish by itself and must be
killed to stop. Basically, the idea is to let it run until one is done inspecting the map.

All files are served locally and only the default map content (roads, buildings, etc.) are loaded from mapbox.
All cloak data is processed locally in JavaScript.

The Map:
[Do not be alarmed if there is no data shown right after load. It initializes to midnight and there is usually no data
present at midnight]

The map shows a combination of information. It's main feature is a heatmap of encounters. With the different sliders
you can choose a day and hour for which you would like to see the heatmap. The data used for the heatmap is always that
of the specified hour only.

The secondary feature is the actual data returned from the cloak. In a zoomed out perspective the actual data is only
visible as very light little rectangles, to indicate where data is located at all. Once you zoom in enough the heatmap
fades out and the rectangles of data records become visible. Each record shows its number of encounters. These
rectangular records are the actual rows the cloak returned. They allow you to check whether the heatmap makes sense and
understand how the heatmap came to be in the first place.


TlDr;
-----
1. Provision conf/cloakConfig.py and conf/mapBoxConfig.py 
2. Run this file from repository base (from the folder this file is in)
3. Wait until it outputs "Serving http at port 8000"
4. Click one of the links it printed before (which and whether they are clickable depends on your console/terminal)
5. Inspect data in web-browser
6. Kill this script
"""

protocolMpi = "https"
hostMpi = "people.mpi-sws.org"
mapBoxPathMpi = "~munz/mapbox"

title = "Encounter heatmap of KL"
cloak = MapBoxCloakAccess()

confLst = list()
for geoWidth in [2**-9, 2**-10, 2**-11, 2**-12]:
    buckets = cloak.piotrEmbarrassingEncounterBuckets(geoWidth)
    confLst.append(MapBoxCreator.createMap(f"encounters-{geoWidth}", f"Lat/Lng width: {geoWidth}", buckets, geoWidth,
                                           geoWidth))

    buckets = cloak.queryEncounterBuckets(geoWidth, geoWidth, raw=True)
    confLst.append(MapBoxCreator.createMap(f"encounters-raw-{geoWidth}", f"Non-anonymized data", buckets, geoWidth, geoWidth, raw=True))
conf = MapBoxCreator.createMergedMap('encounters', title, confLst)

MapBoxCreator.printLinks('Local', title, confLst, conf)
MapBoxCreator.printLinks('Mpi', title, confLst, conf, protocol=protocolMpi, host=hostMpi, port=None,
                         mapBoxPath=mapBoxPathMpi)

MapBoxCreator.serve()
