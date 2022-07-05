import http.server
import socketserver

"""
Utility to crudely share the heatmap prototype
----------------------------------------------

1. `cd` into the dir holding this file
2. `python3 serveMapBox.py`
3. Point browser to http://localhost:8000/www/mapbox/heatmap_conf.html?conf=conf/encounters.json
4. Wait until dust settles
6. Zoom in and out to have things load and become smooth
7. Should be fine now. Looks best at the closest zoom level.

Caveats and todos:
- heatmap coloring is mostly off, I'll be working on so that it looks well regardless of left or right map
- layer visibility needs tweaking, heatmap is visible only in a specific range of zooms
- possibly split the non-anonymized data (left) into varying granularity based on zoom? at least for performance reasons
- performance is very bad, take your time with everything
- during zooming in/out the heatmap looks funky. After zooming wait a few seconds for the render to settle
"""

class MapBoxServer:
    @staticmethod
    def serve():
        handler = http.server.SimpleHTTPRequestHandler
        server = socketserver.TCPServer(("", 8000), handler)
        print("--------------------------------------------------")
        print("Serving http at port 8000")
        server.serve_forever()

MapBoxServer.serve()
