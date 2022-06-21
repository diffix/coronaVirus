import datetime

from cloakConfig import CloakConfig
from sql_adapter import SQLAdapter

commonFilters = "lat != 0 AND lon != 0 AND substring(date, 1, 10) = '2013-01-08'"


class MapBoxCloakAccess:
    def __init__(self):
        self._sqlAdapter = SQLAdapter(CloakConfig.parameters)

    def queryEncounterBuckets(self, lonlatRange, raw=False):
        sql = f"""
SELECT {lonlatRange}::float as lonlatRange, *
                    FROM (SELECT
                          diffix.floor_by(pickup_latitude, {lonlatRange}) as lat,
                          diffix.floor_by(pickup_longitude, {lonlatRange}) as lon,
                          count(*),
                          substring(pickup_datetime, 1, 10) as date,
                          substring(pickup_datetime, 12, 2) as time
                          FROM taxi
                          GROUP BY 1, 2, 4, 5) x
WHERE {commonFilters};
"""
        if raw:
            result = self._sqlAdapter.queryRaw(sql)
        else:
            result = self._sqlAdapter.queryCloak(sql)

        buckets = []
        filtered = 0
        for row in result:
            buckets.append(_rowToBucket(row))
        print(f"Loaded {len(result)} buckets from cloak.")
        print(f"Filtered {filtered} buckets due to */NULL values.")
        self._sqlAdapter.disconnect()
        return buckets

    def piotrEmbarrassingEncounterBuckets(self, lonlatRange):
        # FIXME really want to look at the result first, I'll un-hardcode later
        if lonlatRange == 2**-9:
            sql = f"""
SELECT 0.001953125::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.001953125) as lat,
                         diffix.floor_by(pickup_longitude, 0.001953125) as lon,
                         count(*),
                         substring(pickup_datetime, 1, 10) as date,
                         substring(pickup_datetime, 12, 2) as time
                         FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE {commonFilters};
"""
        elif lonlatRange == 2**-10:
            sql = f"""
(SELECT 0.001953125::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.001953125) as lat,
                         diffix.floor_by(pickup_longitude, 0.001953125) as lon,
                         count(*),
                         substring(pickup_datetime, 1, 10) as date,
                         substring(pickup_datetime, 12, 2) as time
                         FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE {commonFilters}
EXCEPT
SELECT 0.001953125::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.001953125) as lat,
                         diffix.floor_by(pickup_longitude, 0.001953125) as lon,
                         count(*),
                         substring(pickup_datetime, 1, 10) as date,
                         substring(pickup_datetime, 12, 2) as time
                         FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE (lat, lon) IN (SELECT diffix.floor_by(lat_filter, 0.001953125),
                                diffix.floor_by(lon_filter, 0.001953125) 
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.0009765625) as lat_filter,
                         diffix.floor_by(pickup_longitude, 0.0009765625) as lon_filter,
                         substring(pickup_datetime, 1, 10) as date_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3, 4) y)
AND {commonFilters}
)
UNION
SELECT 0.0009765625::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.0009765625) as lat,
                         diffix.floor_by(pickup_longitude, 0.0009765625) as lon,
                         count(*),
                         substring(pickup_datetime, 1, 10) as date,
                         substring(pickup_datetime, 12, 2) as time
                         FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE {commonFilters};
"""

        elif lonlatRange == 2**-11:
            sql = f"""
(SELECT 0.001953125::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.001953125) as lat,
                         diffix.floor_by(pickup_longitude, 0.001953125) as lon,
                         count(*),
                         substring(pickup_datetime, 1, 10) as date,
                         substring(pickup_datetime, 12, 2) as time
                         FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE {commonFilters}
EXCEPT
SELECT 0.001953125::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.001953125) as lat,
                         diffix.floor_by(pickup_longitude, 0.001953125) as lon,
                         count(*),
                         substring(pickup_datetime, 1, 10) as date,
                         substring(pickup_datetime, 12, 2) as time
                         FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE (lat, lon) IN (SELECT diffix.floor_by(lat_filter, 0.001953125),
                                diffix.floor_by(lon_filter, 0.001953125) 
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.0009765625) as lat_filter,
                         diffix.floor_by(pickup_longitude, 0.0009765625) as lon_filter,
                         substring(pickup_datetime, 1, 10) as date_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3, 4) y UNION
                      SELECT diffix.floor_by(lat_filter, 0.001953125),
                                diffix.floor_by(lon_filter, 0.001953125) 
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.00048828125) as lat_filter,
                         diffix.floor_by(pickup_longitude, 0.00048828125) as lon_filter,
                         substring(pickup_datetime, 1, 10) as date_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3, 4) y)
AND {commonFilters}
)
UNION
(SELECT 0.0009765625::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.0009765625) as lat,
                         diffix.floor_by(pickup_longitude, 0.0009765625) as lon,
                         count(*),
                         substring(pickup_datetime, 1, 10) as date,
                         substring(pickup_datetime, 12, 2) as time
                         FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE {commonFilters}
EXCEPT
SELECT 0.0009765625::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.0009765625) as lat,
                         diffix.floor_by(pickup_longitude, 0.0009765625) as lon,
                         count(*),
                         substring(pickup_datetime, 1, 10) as date,
                         substring(pickup_datetime, 12, 2) as time
                         FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE (lat, lon) IN (SELECT diffix.floor_by(lat_filter, 0.0009765625),
                                diffix.floor_by(lon_filter, 0.0009765625) 
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.00048828125) as lat_filter,
                         diffix.floor_by(pickup_longitude, 0.00048828125) as lon_filter,
                         substring(pickup_datetime, 1, 10) as date_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3, 4) y)
AND {commonFilters}
)
UNION
SELECT 0.00048828125::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.00048828125) as lat,
                         diffix.floor_by(pickup_longitude, 0.00048828125) as lon,
                         count(*),
                         substring(pickup_datetime, 1, 10) as date,
                         substring(pickup_datetime, 12, 2) as time
                         FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE {commonFilters};
"""
        elif lonlatRange == 2**-12:
            sql = f"""
(SELECT 0.001953125::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.001953125) as lat,
                         diffix.floor_by(pickup_longitude, 0.001953125) as lon,
                         count(*),
                         substring(pickup_datetime, 1, 10) as date,
                         substring(pickup_datetime, 12, 2) as time
                         FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE {commonFilters}
EXCEPT
SELECT 0.001953125::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.001953125) as lat,
                         diffix.floor_by(pickup_longitude, 0.001953125) as lon,
                         count(*),
                         substring(pickup_datetime, 1, 10) as date,
                         substring(pickup_datetime, 12, 2) as time
                         FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE (lat, lon) IN (SELECT diffix.floor_by(lat_filter, 0.001953125),
                                diffix.floor_by(lon_filter, 0.001953125) 
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.0009765625) as lat_filter,
                         diffix.floor_by(pickup_longitude, 0.0009765625) as lon_filter,
                         substring(pickup_datetime, 1, 10) as date_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3, 4) y UNION 
                      SELECT diffix.floor_by(lat_filter, 0.001953125),
                                diffix.floor_by(lon_filter, 0.001953125) 
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.00048828125) as lat_filter,
                         diffix.floor_by(pickup_longitude, 0.00048828125) as lon_filter,
                         substring(pickup_datetime, 1, 10) as date_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3, 4) y UNION
                      SELECT diffix.floor_by(lat_filter, 0.001953125),
                                diffix.floor_by(lon_filter, 0.001953125) 
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.000244140625) as lat_filter,
                         diffix.floor_by(pickup_longitude, 0.000244140625) as lon_filter,
                         substring(pickup_datetime, 1, 10) as date_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3, 4) y)
AND {commonFilters}
)
UNION
(SELECT 0.0009765625::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.0009765625) as lat,
                         diffix.floor_by(pickup_longitude, 0.0009765625) as lon,
                         count(*),
                         substring(pickup_datetime, 1, 10) as date,
                         substring(pickup_datetime, 12, 2) as time
                         FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE {commonFilters}
EXCEPT
SELECT 0.0009765625::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.0009765625) as lat,
                         diffix.floor_by(pickup_longitude, 0.0009765625) as lon,
                         count(*),
                         substring(pickup_datetime, 1, 10) as date,
                         substring(pickup_datetime, 12, 2) as time
                         FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE (lat, lon) IN (SELECT diffix.floor_by(lat_filter, 0.0009765625),
                                diffix.floor_by(lon_filter, 0.0009765625) 
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.00048828125) as lat_filter,
                         diffix.floor_by(pickup_longitude, 0.00048828125) as lon_filter,
                         substring(pickup_datetime, 1, 10) as date_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3, 4) y UNION
                     SELECT diffix.floor_by(lat_filter, 0.0009765625),
                                diffix.floor_by(lon_filter, 0.0009765625) 
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.000244140625) as lat_filter,
                         diffix.floor_by(pickup_longitude, 0.000244140625) as lon_filter,
                         substring(pickup_datetime, 1, 10) as date_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3, 4) y)
AND {commonFilters}
)
UNION
(SELECT 0.00048828125::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.00048828125) as lat,
                         diffix.floor_by(pickup_longitude, 0.00048828125) as lon,
                         count(*),
                         substring(pickup_datetime, 1, 10) as date,
                         substring(pickup_datetime, 12, 2) as time
                         FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE {commonFilters}
EXCEPT
SELECT 0.00048828125::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.00048828125) as lat,
                         diffix.floor_by(pickup_longitude, 0.00048828125) as lon,
                         count(*),
                         substring(pickup_datetime, 1, 10) as date,
                         substring(pickup_datetime, 12, 2) as time
                         FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE (lat, lon) IN (SELECT diffix.floor_by(lat_filter, 0.00048828125),
                                diffix.floor_by(lon_filter, 0.00048828125) 
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.000244140625) as lat_filter,
                         diffix.floor_by(pickup_longitude, 0.000244140625) as lon_filter,
                         substring(pickup_datetime, 1, 10) as date_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3, 4) y)
AND {commonFilters}
)
UNION
SELECT 0.000244140625::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, 0.000244140625) as lat,
                         diffix.floor_by(pickup_longitude, 0.000244140625) as lon,
                         count(*),
                         substring(pickup_datetime, 1, 10) as date,
                         substring(pickup_datetime, 12, 2) as time
                         FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE {commonFilters};
"""
        result = self._sqlAdapter.queryCloak(sql)

        buckets = []
        filtered = 0
        for row in result:
            buckets.append(_rowToBucket(row))
        print(f"Loaded {len(result)} buckets from cloak.")
        print(f"Filtered {filtered} buckets due to */NULL values.")
        self._sqlAdapter.disconnect()
        return buckets

# FIXME again: refactor
def _rowToBucket(row):
    lonlatRange = row[0]
    # FIXME a bit silly, find the correct formula
    rangeArea = lonlatRange ** 2
    lat = row[1]
    lon = row[2]
    count = row[3]
    date = datetime.datetime.fromisoformat(row[4])
    time = date.combine(date, datetime.time(hour=int(row[5])))
    return MapBoxBucket(
        lat,
        lon,
        time=time,
        count=count,
        lonlatRange=lonlatRange
    )


class MapBoxBucket:
    def __init__(self, lat, lon, time=None, count=-1, lonlatRange=None):
        self.lat = lat
        self.lon = lon
        self.time = time
        self.count = count
        self.lonlatRange = lonlatRange

    def __str__(self):
        return f"MapBoxEncounters: {self.listOfStrings()}"

    __repr__ = __str__

    def listOfStrings(self):
        return [f"{v}" for v in [self.lat, self.lon, self.time, self.count, self.lonlatRange] if v is not None]
