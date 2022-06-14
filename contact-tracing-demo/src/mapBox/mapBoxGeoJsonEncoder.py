class MapBoxGeoJsonEncoder:
    @staticmethod
    def _encodeAsPolygon(lat, lon, latWidth, lonWidth):
        return {
            'type': 'Polygon',
            'coordinates': [
                [
                    [round(lon, 6), round(lat, 6)],
                    [round(lon + lonWidth, 6), round(lat, 6)],
                    [round(lon + lonWidth, 6), round(lat + latWidth, 6)],
                    [round(lon, 6), round(lat + latWidth, 6)],
                    [round(lon, 6), round(lat, 6)]
                ]
            ]
        }

    @staticmethod
    def _encodeAsPoint(lat, lon, latWidth, lonWidth):
        return {
            'type': 'Point',
            'coordinates': [round(lon + lonWidth / 2.0, 6), round(lat + latWidth / 2.0, 6)]
        }

    @staticmethod
    def encodeSingle(bucket, latWidth, lonWidth, asPoint=False):
        if bucket.lonlatRange:
            latWidth = bucket.lonlatRange
            lonWidth = bucket.lonlatRange
        return {
            'geometry': MapBoxGeoJsonEncoder._encodeAsPoint(bucket.lat, bucket.lon, latWidth, lonWidth) if asPoint else
            MapBoxGeoJsonEncoder._encodeAsPolygon(bucket.lat, bucket.lon, latWidth, lonWidth),
            'type': 'Feature',
            'properties': {
                'time': round(bucket.time.timestamp()) if bucket.time is not None else -1,
                'encounters': bucket.count,
                'encounters_density': bucket.density,
                'lonlat_range': bucket.lonlatRange
            }
        }

    @staticmethod
    def encodeMany(buckets, latWidth, lonWidth, asPoints=False):
        return {
            "type": "FeatureCollection",
            "features": [MapBoxGeoJsonEncoder.encodeSingle(b, latWidth, lonWidth, asPoints) for b in buckets]
        }
