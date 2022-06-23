import datetime

from cloakConfig import CloakConfig
from sql_adapter import SQLAdapter

commonFilters = "lat != 0 AND lon != 0 AND substring(date, 1, 10) = '2013-01-08'"
commonFiltersFilter = "substring(date_filter, 1, 10) = '2013-01-08'"


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
                          substring(pickup_datetime, 12, 2) as time,
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8
                          FROM taxi
                          GROUP BY 1, 2, 4, 5) x
WHERE {commonFilters};
"""
        if raw:
            result = self._sqlAdapter.queryRaw(sql)
        else:
            result = self._sqlAdapter.queryCloak(sql)

        buckets = []
        for row in result:
            buckets.append(_rowToBucket(row))
        print(f"Loaded {len(result)} raw buckets with range {lonlatRange}.")
        self._sqlAdapter.disconnect()
        return buckets

    def piotrEmbarrassingEncounterBuckets(self, lonlatRange, lonlatRanges):
        # FIXME really want to look at the result first, I'll un-hardcode later
        if lonlatRange == lonlatRanges[0]:
            sql = f"""
SELECT {lonlatRange}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange}) as lon,
                          count(*),
                          substring(pickup_datetime, 1, 10) as date,
                          substring(pickup_datetime, 12, 2) as time,
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE {commonFilters};
"""
        elif lonlatRange == lonlatRanges[1]:
            sql = f"""
(SELECT {lonlatRange * 2}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 2}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 2}) as lon,
                          count(*),
                          substring(pickup_datetime, 1, 10) as date,
                          substring(pickup_datetime, 12, 2) as time,
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE {commonFilters}
EXCEPT
SELECT {lonlatRange * 2}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 2}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 2}) as lon,
                          count(*),
                          substring(pickup_datetime, 1, 10) as date,
                          substring(pickup_datetime, 12, 2) as time,
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE (lat, lon, time) IN (SELECT diffix.floor_by(lat_filter, {lonlatRange * 2}),
                            diffix.floor_by(lon_filter, {lonlatRange * 2}),
                            time_filter
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange}) as lat_filter,
                         diffix.floor_by(pickup_longitude, {lonlatRange}) as lon_filter,
                         substring(pickup_datetime, 1, 10) as date_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3, 4) y
                        WHERE {commonFiltersFilter}
                    )
AND {commonFilters}
)
UNION
SELECT {lonlatRange}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange}) as lon,
                          count(*),
                          substring(pickup_datetime, 1, 10) as date,
                          substring(pickup_datetime, 12, 2) as time,
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE {commonFilters};
"""

        elif lonlatRange == lonlatRanges[2]:
            sql = f"""
(SELECT {lonlatRange * 4}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 4}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 4}) as lon,
                          count(*),
                          substring(pickup_datetime, 1, 10) as date,
                          substring(pickup_datetime, 12, 2) as time,
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE {commonFilters}
EXCEPT
SELECT {lonlatRange * 4}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 4}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 4}) as lon,
                          count(*),
                          substring(pickup_datetime, 1, 10) as date,
                          substring(pickup_datetime, 12, 2) as time,
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE (lat, lon, time) IN (SELECT diffix.floor_by(lat_filter, {lonlatRange * 4}),
                            diffix.floor_by(lon_filter, {lonlatRange * 4}),
                            time_filter 
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 2}) as lat_filter,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 2}) as lon_filter,
                         substring(pickup_datetime, 1, 10) as date_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3, 4) y
                        WHERE {commonFiltersFilter}
                     UNION
                      SELECT diffix.floor_by(lat_filter, {lonlatRange * 4}),
                             diffix.floor_by(lon_filter, {lonlatRange * 4}),
                             time_filter
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange}) as lat_filter,
                         diffix.floor_by(pickup_longitude, {lonlatRange}) as lon_filter,
                         substring(pickup_datetime, 1, 10) as date_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3, 4) y
                        WHERE {commonFiltersFilter}
                    )
AND {commonFilters}
)
UNION
(SELECT {lonlatRange * 2}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 2}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 2}) as lon,
                          count(*),
                          substring(pickup_datetime, 1, 10) as date,
                          substring(pickup_datetime, 12, 2) as time,
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE {commonFilters}
EXCEPT
SELECT {lonlatRange * 2}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 2}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 2}) as lon,
                          count(*),
                          substring(pickup_datetime, 1, 10) as date,
                          substring(pickup_datetime, 12, 2) as time,
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE (lat, lon, time) IN (SELECT diffix.floor_by(lat_filter, {lonlatRange * 2}),
                            diffix.floor_by(lon_filter, {lonlatRange * 2}),
                            time_filter
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange}) as lat_filter,
                         diffix.floor_by(pickup_longitude, {lonlatRange}) as lon_filter,
                         substring(pickup_datetime, 1, 10) as date_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3, 4) y
                        WHERE {commonFiltersFilter}
                    )
AND {commonFilters}
)
UNION
SELECT {lonlatRange}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange}) as lon,
                          count(*),
                          substring(pickup_datetime, 1, 10) as date,
                          substring(pickup_datetime, 12, 2) as time,
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE {commonFilters};
"""
        elif lonlatRange == lonlatRanges[3]:
            sql = f"""
(SELECT {lonlatRange * 8}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 8}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 8}) as lon,
                          count(*),
                          substring(pickup_datetime, 1, 10) as date,
                          substring(pickup_datetime, 12, 2) as time,
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE {commonFilters}
EXCEPT
SELECT {lonlatRange * 8}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 8}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 8}) as lon,
                          count(*),
                          substring(pickup_datetime, 1, 10) as date,
                          substring(pickup_datetime, 12, 2) as time,
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE (lat, lon, time) IN (SELECT diffix.floor_by(lat_filter, {lonlatRange * 8}),
                            diffix.floor_by(lon_filter, {lonlatRange * 8}),
                            time_filter
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 4}) as lat_filter,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 4}) as lon_filter,
                         substring(pickup_datetime, 1, 10) as date_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3, 4) y
                        WHERE {commonFiltersFilter}
                     UNION 
                      SELECT diffix.floor_by(lat_filter, {lonlatRange * 8}),
                             diffix.floor_by(lon_filter, {lonlatRange * 8}),
                             time_filter
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 2}) as lat_filter,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 2}) as lon_filter,
                         substring(pickup_datetime, 1, 10) as date_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3, 4) y
                        WHERE {commonFiltersFilter}
                     UNION
                      SELECT diffix.floor_by(lat_filter, {lonlatRange * 8}),
                             diffix.floor_by(lon_filter, {lonlatRange * 8}),
                             time_filter
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange}) as lat_filter,
                         diffix.floor_by(pickup_longitude, {lonlatRange}) as lon_filter,
                         substring(pickup_datetime, 1, 10) as date_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3, 4) y
                        WHERE {commonFiltersFilter}
                    )
AND {commonFilters}
)
UNION
(SELECT {lonlatRange * 4}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 4}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 4}) as lon,
                          count(*),
                          substring(pickup_datetime, 1, 10) as date,
                          substring(pickup_datetime, 12, 2) as time,
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE {commonFilters}
EXCEPT
SELECT {lonlatRange * 4}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 4}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 4}) as lon,
                          count(*),
                          substring(pickup_datetime, 1, 10) as date,
                          substring(pickup_datetime, 12, 2) as time,
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE (lat, lon, time) IN (SELECT diffix.floor_by(lat_filter, {lonlatRange * 4}),
                            diffix.floor_by(lon_filter, {lonlatRange * 4}),
                            time_filter
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 2}) as lat_filter,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 2}) as lon_filter,
                         substring(pickup_datetime, 1, 10) as date_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3, 4) y
                        WHERE {commonFiltersFilter}
                     UNION
                     SELECT diffix.floor_by(lat_filter, {lonlatRange * 4}),
                            diffix.floor_by(lon_filter, {lonlatRange * 4}),
                            time_filter
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange}) as lat_filter,
                         diffix.floor_by(pickup_longitude, {lonlatRange}) as lon_filter,
                         substring(pickup_datetime, 1, 10) as date_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3, 4) y
                        WHERE {commonFiltersFilter}
                    )
AND {commonFilters}
)
UNION
(SELECT {lonlatRange * 2}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 2}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 2}) as lon,
                          count(*),
                          substring(pickup_datetime, 1, 10) as date,
                          substring(pickup_datetime, 12, 2) as time,
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE {commonFilters}
EXCEPT
SELECT {lonlatRange * 2}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 2}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 2}) as lon,
                          count(*),
                          substring(pickup_datetime, 1, 10) as date,
                          substring(pickup_datetime, 12, 2) as time,
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE (lat, lon, time) IN (SELECT diffix.floor_by(lat_filter, {lonlatRange * 2}),
                            diffix.floor_by(lon_filter, {lonlatRange * 2}),
                            time_filter
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange}) as lat_filter,
                         diffix.floor_by(pickup_longitude, {lonlatRange}) as lon_filter,
                         substring(pickup_datetime, 1, 10) as date_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3, 4) y
                        WHERE {commonFiltersFilter}
                    )
AND {commonFilters}
)
UNION
SELECT {lonlatRange}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange}) as lon,
                          count(*),
                          substring(pickup_datetime, 1, 10) as date,
                          substring(pickup_datetime, 12, 2) as time,
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 4, 5) x
WHERE {commonFilters};
"""
        result = self._sqlAdapter.queryCloak(sql)

        buckets = []
        for row in result:
            buckets.append(_rowToBucket(row))
        print(f"Loaded {len(result)} anon buckets with range {lonlatRange}.")
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
    fareAmounts = row[6]
    return MapBoxBucket(
        lat,
        lon,
        time=time,
        count=count,
        lonlatRange=lonlatRange,
        fareAmounts=fareAmounts
    )


class MapBoxBucket:
    def __init__(self, lat, lon, time=None, count=-1, lonlatRange=None, fareAmounts=None):
        self.lat = lat
        self.lon = lon
        self.time = time
        self.count = count
        self.lonlatRange = lonlatRange
        self.fareAmounts = fareAmounts

    def __str__(self):
        return f"MapBoxEncounters: {self.listOfStrings()}"

    __repr__ = __str__

    def listOfStrings(self):
        return [f"{v}" for v in [self.lat, self.lon, self.time, self.count, self.lonlatRange, self.fareAmounts] if v is not None]
