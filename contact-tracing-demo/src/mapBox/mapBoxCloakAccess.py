import datetime

from cloakConfig import CloakConfig
from sql_adapter import SQLAdapter


class MapBoxCloakAccess:
    def __init__(self):
        self._sqlAdapter = SQLAdapter(CloakConfig.parameters)

    def queryEncounterBuckets(self, latRange, lonRange, timeRange=None, raw=False):
        # FIXME a bit silly, find the correct formula
        rangeArea = latRange * lonRange
        sql = f"SELECT diffix.floor_by(pickup_latitude, {latRange}) as lat, diffix.floor_by(pickup_longitude, {lonRange}) as lon, "
        groupBy = "1,2"
        if timeRange is not None:
            allowed = {'year', 'quarter', 'month', 'day', 'hour', 'minute', 'second'}
            if timeRange not in allowed:
                raise ValueError(f"timeRange {timeRange} must be one of {allowed}")
            sql += f"DATE_TRUNC('{timeRange}', time), "
            groupBy += ",3"
        sql += f"COUNT(*) FROM taxi GROUP BY {groupBy};"
        if raw:
            result = self._sqlAdapter.queryRaw(sql)
        else:
            result = self._sqlAdapter.queryCloak(sql)

        buckets = []
        filtered = 0
        for row in result:
            buckets.append(_rowToBucket(row, rangeArea))
        print(f"Loaded {len(result)} buckets from cloak.")
        print(f"Filtered {filtered} buckets due to */NULL values.")
        self._sqlAdapter.disconnect()
        return buckets

    def piotrEmbarrassingEncounterBuckets(self, lonlatRange):
        # FIXME a bit silly, find the correct formula
        rangeArea = lonlatRange * lonlatRange
        # FIXME really want to look at the result first, I'll un-hardcode later
        if lonlatRange == 2**-9:
            sql = """
SELECT 0.001953125::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.001953125) as lat,
                         diffix.floor_by(pickup_longitude, 0.001953125) as lon,
                         count(*)
                         FROM taxi
                         GROUP BY 1, 2) x
WHERE lat != 0 AND lon != 0;
"""
        elif lonlatRange == 2**-10:
            sql = """
SELECT 0.001953125::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.001953125) as lat,
                         diffix.floor_by(pickup_longitude, 0.001953125) as lon,
                         count(*)
                         FROM taxi
                         GROUP BY 1, 2) x
WHERE NOT (lat, lon) IN (SELECT 
                         diffix.floor_by(pickup_latitude, 0.0009765625),
                         diffix.floor_by(pickup_longitude, 0.0009765625)
                         FROM taxi
                         GROUP BY 1, 2)
AND lat != 0 AND lon != 0
UNION
SELECT 0.0009765625::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.0009765625) as lat,
                         diffix.floor_by(pickup_longitude, 0.0009765625) as lon,
                         count(*)
                         FROM taxi
                         GROUP BY 1, 2) x
WHERE lat != 0 AND lon != 0;
"""

        elif lonlatRange == 2**-11:
            sql = """
SELECT 0.001953125::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.001953125) as lat,
                         diffix.floor_by(pickup_longitude, 0.001953125) as lon,
                         count(*)
                         FROM taxi
                         GROUP BY 1, 2) x
WHERE NOT (lat, lon) IN (SELECT 
                         diffix.floor_by(pickup_latitude, 0.0009765625),
                         diffix.floor_by(pickup_longitude, 0.0009765625)
                         FROM taxi
                         GROUP BY 1, 2)
AND NOT (lat, lon) IN (SELECT 
                         diffix.floor_by(pickup_latitude, 0.00048828125),
                         diffix.floor_by(pickup_longitude, 0.00048828125)
                         FROM taxi
                         GROUP BY 1, 2)
AND lat != 0 AND lon != 0
UNION
SELECT 0.0009765625::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.0009765625) as lat,
                         diffix.floor_by(pickup_longitude, 0.0009765625) as lon,
                         count(*)
                         FROM taxi
                         GROUP BY 1, 2) x
WHERE NOT (lat, lon) IN (SELECT 
                         diffix.floor_by(pickup_latitude, 0.00048828125),
                         diffix.floor_by(pickup_longitude, 0.00048828125)
                         FROM taxi
                         GROUP BY 1, 2)
AND lat != 0 AND lon != 0
UNION
SELECT 0.00048828125::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.00048828125) as lat,
                         diffix.floor_by(pickup_longitude, 0.00048828125) as lon,
                         count(*)
                         FROM taxi
                         GROUP BY 1, 2) x
WHERE lat != 0 AND lon != 0;
"""
        elif lonlatRange == 2**-12:
            sql = """
SELECT 0.001953125::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.001953125) as lat,
                         diffix.floor_by(pickup_longitude, 0.001953125) as lon,
                         count(*)
                         FROM taxi
                         GROUP BY 1, 2) x
WHERE NOT (lat, lon) IN (SELECT 
                         diffix.floor_by(pickup_latitude, 0.0009765625),
                         diffix.floor_by(pickup_longitude, 0.0009765625)
                         FROM taxi
                         GROUP BY 1, 2)
AND NOT (lat, lon) IN (SELECT 
                         diffix.floor_by(pickup_latitude, 0.00048828125),
                         diffix.floor_by(pickup_longitude, 0.00048828125)
                         FROM taxi
                         GROUP BY 1, 2)
AND NOT (lat, lon) IN (SELECT 
                         diffix.floor_by(pickup_latitude, 0.000244140625),
                         diffix.floor_by(pickup_longitude, 0.000244140625)
                         FROM taxi
                         GROUP BY 1, 2)
AND lat != 0 AND lon != 0
UNION
SELECT 0.0009765625::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.0009765625) as lat,
                         diffix.floor_by(pickup_longitude, 0.0009765625) as lon,
                         count(*)
                         FROM taxi
                         GROUP BY 1, 2) x
WHERE NOT (lat, lon) IN (SELECT 
                         diffix.floor_by(pickup_latitude, 0.00048828125),
                         diffix.floor_by(pickup_longitude, 0.00048828125)
                         FROM taxi
                         GROUP BY 1, 2)
AND NOT (lat, lon) IN (SELECT 
                         diffix.floor_by(pickup_latitude, 0.000244140625),
                         diffix.floor_by(pickup_longitude, 0.000244140625)
                         FROM taxi
                         GROUP BY 1, 2)
AND lat != 0 AND lon != 0
UNION
SELECT 0.00048828125::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.00048828125) as lat,
                         diffix.floor_by(pickup_longitude, 0.00048828125) as lon,
                         count(*)
                         FROM taxi
                         GROUP BY 1, 2) x
WHERE NOT (lat, lon) IN (SELECT 
                         diffix.floor_by(pickup_latitude, 0.000244140625),
                         diffix.floor_by(pickup_longitude, 0.000244140625)
                         FROM taxi
                         GROUP BY 1, 2)
AND lat != 0 AND lon != 0
UNION
SELECT 0.000244140625::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.000244140625) as lat,
                         diffix.floor_by(pickup_longitude, 0.000244140625) as lon,
                         count(*)
                         FROM taxi
                         GROUP BY 1, 2) x
WHERE lat != 0 AND lon != 0;
"""
        result = self._sqlAdapter.queryCloak(sql)

        buckets = []
        filtered = 0
        for row in result:
            buckets.append(_rowToBucket2(row, rangeArea))
        print(f"Loaded {len(result)} buckets from cloak.")
        print(f"Filtered {filtered} buckets due to */NULL values.")
        self._sqlAdapter.disconnect()
        return buckets

def _rowToBucket(row, rangeArea):
    lat = row[0]
    lon = row[1]
    # time = None
    time = datetime.datetime.fromtimestamp(0)
    if 3 < len(row):
        time = row[2]
    return MapBoxBucket(
        lat,
        lon,
        time=time,
        count=row[len(row) - 1],
        density=row[len(row) - 1] / rangeArea / 250000
    )

# FIXME again: refactor
def _rowToBucket2(row, rangeArea):
    lonlatRange = row[0]
    lat = row[1]
    lon = row[2]
    # time = None
    time = datetime.datetime.fromtimestamp(0)
    return MapBoxBucket(
        lat,
        lon,
        time=time,
        count=row[len(row) - 1],
        density=row[len(row) - 1] / rangeArea / 250000,
        lonlatRange=lonlatRange
    )


class MapBoxBucket:
    def __init__(self, lat, lon, time=None, count=-1, density=-1, lonlatRange=None):
        self.lat = lat
        self.lon = lon
        self.time = time
        self.count = count
        self.density = density
        self.lonlatRange = lonlatRange

    def __str__(self):
        return f"MapBoxEncounters: {self.listOfStrings()}"

    __repr__ = __str__

    def listOfStrings(self):
        return [f"{v}" for v in [self.lat, self.lon, self.time, self.count, self.density, self.lonlatRange] if v is not None]
