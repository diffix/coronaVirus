import datetime

from cloakConfig import CloakConfig
from sql_adapter import SQLAdapter


class MapBoxCloakAccess:
    def __init__(self):
        self._sqlAdapter = SQLAdapter(CloakConfig.parameters)

    def queryEncounterBuckets(self, lonlatRange, raw=False):
        sql = f"""
SELECT {lonlatRange}::float as lonlatRange, *
                    FROM (SELECT
                          diffix.floor_by(pickup_latitude, {lonlatRange}) as lat,
                          diffix.floor_by(pickup_longitude, {lonlatRange}) as lon,
                          substring(pickup_datetime, 12, 2) as time,
                          count(*),
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round((sum(trip_distance) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round(avg(fare_amount)::numeric, 2)::float8
                          FROM taxi
                          GROUP BY 1, 2, 3) x;
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
                          substring(pickup_datetime, 12, 2) as time,
                          count(*),
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round((sum(trip_distance) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round(avg(fare_amount)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 3) x;
"""
        elif lonlatRange == lonlatRanges[1]:
            sql = f"""
(SELECT {lonlatRange * 2}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 2}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 2}) as lon,
                          substring(pickup_datetime, 12, 2) as time,
                          count(*),
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round((sum(trip_distance) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round(avg(fare_amount)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 3) x
EXCEPT
SELECT {lonlatRange * 2}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 2}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 2}) as lon,
                          substring(pickup_datetime, 12, 2) as time,
                          count(*),
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round((sum(trip_distance) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round(avg(fare_amount)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 3) x
WHERE (lat, lon, time) IN (SELECT diffix.floor_by(lat_filter, {lonlatRange * 2}),
                            diffix.floor_by(lon_filter, {lonlatRange * 2}),
                            time_filter
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange}) as lat_filter,
                         diffix.floor_by(pickup_longitude, {lonlatRange}) as lon_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3) y
                        
                    )
)
UNION
SELECT {lonlatRange}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange}) as lon,
                          substring(pickup_datetime, 12, 2) as time,
                          count(*),
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round((sum(trip_distance) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round(avg(fare_amount)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 3) x;
"""

        elif lonlatRange == lonlatRanges[2]:
            sql = f"""
(SELECT {lonlatRange * 4}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 4}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 4}) as lon,
                          substring(pickup_datetime, 12, 2) as time,
                          count(*),
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round((sum(trip_distance) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round(avg(fare_amount)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 3) x
EXCEPT
SELECT {lonlatRange * 4}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 4}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 4}) as lon,
                          substring(pickup_datetime, 12, 2) as time,
                          count(*),
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round((sum(trip_distance) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round(avg(fare_amount)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 3) x
WHERE (lat, lon, time) IN (SELECT diffix.floor_by(lat_filter, {lonlatRange * 4}),
                            diffix.floor_by(lon_filter, {lonlatRange * 4}),
                            time_filter 
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 2}) as lat_filter,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 2}) as lon_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3) y
                        
                     UNION
                      SELECT diffix.floor_by(lat_filter, {lonlatRange * 4}),
                             diffix.floor_by(lon_filter, {lonlatRange * 4}),
                             time_filter
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange}) as lat_filter,
                         diffix.floor_by(pickup_longitude, {lonlatRange}) as lon_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3) y
                        
                    )
)
UNION
(SELECT {lonlatRange * 2}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 2}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 2}) as lon,
                          substring(pickup_datetime, 12, 2) as time,
                          count(*),
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round((sum(trip_distance) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round(avg(fare_amount)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 3) x
EXCEPT
SELECT {lonlatRange * 2}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 2}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 2}) as lon,
                          substring(pickup_datetime, 12, 2) as time,
                          count(*),
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round((sum(trip_distance) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round(avg(fare_amount)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 3) x
WHERE (lat, lon, time) IN (SELECT diffix.floor_by(lat_filter, {lonlatRange * 2}),
                            diffix.floor_by(lon_filter, {lonlatRange * 2}),
                            time_filter
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange}) as lat_filter,
                         diffix.floor_by(pickup_longitude, {lonlatRange}) as lon_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3) y
                        
                    )
)
UNION
SELECT {lonlatRange}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange}) as lon,
                          substring(pickup_datetime, 12, 2) as time,
                          count(*),
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round((sum(trip_distance) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round(avg(fare_amount)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 3) x;
"""
        elif lonlatRange == lonlatRanges[3]:
            sql = f"""
(SELECT {lonlatRange * 8}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 8}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 8}) as lon,
                          substring(pickup_datetime, 12, 2) as time,
                          count(*),
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round((sum(trip_distance) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round(avg(fare_amount)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 3) x
EXCEPT
SELECT {lonlatRange * 8}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 8}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 8}) as lon,
                          substring(pickup_datetime, 12, 2) as time,
                          count(*),
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round((sum(trip_distance) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round(avg(fare_amount)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 3) x
WHERE (lat, lon, time) IN (SELECT diffix.floor_by(lat_filter, {lonlatRange * 8}),
                            diffix.floor_by(lon_filter, {lonlatRange * 8}),
                            time_filter
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 4}) as lat_filter,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 4}) as lon_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3) y
                        
                     UNION 
                      SELECT diffix.floor_by(lat_filter, {lonlatRange * 8}),
                             diffix.floor_by(lon_filter, {lonlatRange * 8}),
                             time_filter
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 2}) as lat_filter,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 2}) as lon_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3) y
                        
                     UNION
                      SELECT diffix.floor_by(lat_filter, {lonlatRange * 8}),
                             diffix.floor_by(lon_filter, {lonlatRange * 8}),
                             time_filter
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange}) as lat_filter,
                         diffix.floor_by(pickup_longitude, {lonlatRange}) as lon_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3) y
                        
                    )
)
UNION
(SELECT {lonlatRange * 4}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 4}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 4}) as lon,
                          substring(pickup_datetime, 12, 2) as time,
                          count(*),
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round((sum(trip_distance) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round(avg(fare_amount)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 3) x
EXCEPT
SELECT {lonlatRange * 4}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 4}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 4}) as lon,
                          substring(pickup_datetime, 12, 2) as time,
                          count(*),
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round((sum(trip_distance) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round(avg(fare_amount)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 3) x
WHERE (lat, lon, time) IN (SELECT diffix.floor_by(lat_filter, {lonlatRange * 4}),
                            diffix.floor_by(lon_filter, {lonlatRange * 4}),
                            time_filter
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 2}) as lat_filter,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 2}) as lon_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3) y
                        
                     UNION
                     SELECT diffix.floor_by(lat_filter, {lonlatRange * 4}),
                            diffix.floor_by(lon_filter, {lonlatRange * 4}),
                            time_filter
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange}) as lat_filter,
                         diffix.floor_by(pickup_longitude, {lonlatRange}) as lon_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3) y
                        
                    )
)
UNION
(SELECT {lonlatRange * 2}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 2}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 2}) as lon,
                          substring(pickup_datetime, 12, 2) as time,
                          count(*),
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round((sum(trip_distance) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round(avg(fare_amount)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 3) x
EXCEPT
SELECT {lonlatRange * 2}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange * 2}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange * 2}) as lon,
                          substring(pickup_datetime, 12, 2) as time,
                          count(*),
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round((sum(trip_distance) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round(avg(fare_amount)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 3) x
WHERE (lat, lon, time) IN (SELECT diffix.floor_by(lat_filter, {lonlatRange * 2}),
                            diffix.floor_by(lon_filter, {lonlatRange * 2}),
                            time_filter
                        FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange}) as lat_filter,
                         diffix.floor_by(pickup_longitude, {lonlatRange}) as lon_filter,
                         substring(pickup_datetime, 12, 2) as time_filter
                         FROM taxi
                         GROUP BY 1, 2, 3) y
                        
                    )
)
UNION
SELECT {lonlatRange}::float as lonlatRange, * 
                   FROM (SELECT 
                         diffix.floor_by(pickup_latitude, {lonlatRange}) as lat,
                         diffix.floor_by(pickup_longitude, {lonlatRange}) as lon,
                          substring(pickup_datetime, 12, 2) as time,
                          count(*),
                          round((sum(fare_amount) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round((sum(trip_distance) / NULLIF(sum(trip_time_in_secs), 0) * 3600)::numeric, 2)::float8,
                          round(avg(fare_amount)::numeric, 2)::float8
                          FROM taxi
                         GROUP BY 1, 2, 3) x;
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
    # FIXME: if we end up doing this like that (aggregating hour-by-hour data for entire range of dates)
    #        we should rather export the hour, not the datetime as timestamp
    date = datetime.datetime(year=2013, month=1, day=1)
    time = date.combine(date, datetime.time(hour=int(row[3])))
    count = row[4]
    hourlyRates = row[5]
    tripSpeed = row[6]
    fareAmounts = row[7]
    return MapBoxBucket(
        lat,
        lon,
        time=time,
        count=count,
        lonlatRange=lonlatRange,
        hourlyRates=hourlyRates,
        tripSpeed=tripSpeed,
        fareAmounts=fareAmounts
    )


class MapBoxBucket:
    def __init__(self, lat, lon, time=None, count=-1, lonlatRange=None, hourlyRates=None, tripSpeed=None, fareAmounts=None):
        self.lat = lat
        self.lon = lon
        self.time = time
        self.count = count
        self.lonlatRange = lonlatRange
        self.hourlyRates = hourlyRates
        self.tripSpeed = tripSpeed
        self.fareAmounts = fareAmounts

    def __str__(self):
        return f"MapBoxEncounters: {self.listOfStrings()}"

    __repr__ = __str__

    def listOfStrings(self):
        return [f"{v}" for v in [self.lat, self.lon, self.time, self.count, self.lonlatRange, self.hourlyRates, self.tripSpeed,
                                 self.fareAmounts] if v is not None]
