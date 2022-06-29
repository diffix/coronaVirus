import datetime
import copy

from cloakConfig import CloakConfig
from sql_adapter import SQLAdapter

def _sql(lonlatRange, countThresh=0):
    return f"""
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
                            GROUP BY 1, 2, 3
                            HAVING count(*) >= {countThresh}) x
WHERE time::integer % 4 = 0;
"""

def _lonlatSteps(start, parentRange, childRange):
    nSteps = round(parentRange / childRange)
    return [start + i * childRange for i in range(0, nSteps)]


class MapBoxCloakAccess:
    def __init__(self):
        self._sqlAdapter = SQLAdapter(CloakConfig.parameters)

    def queryAndStackBuckets(self, lonlatRange, parentBuckets, raw=False):
        sql = _sql(lonlatRange, countThresh=5 if raw else 0)
        if raw:
            result = self._sqlAdapter.queryRaw(sql)
        else:
            result = self._sqlAdapter.queryCloak(sql)

        buckets = []
        for row in result:
            buckets.append(_rowToBucket(row))
        print(f"Loaded {len(buckets)} {'raw' if raw else 'anon'} buckets with range {lonlatRange}.")

        if parentBuckets:
            bucketsByLatlon = {}
            for bucket in buckets:
                bucketsByLatlon[(bucket.lat, bucket.lon, bucket.time)] = True

            for parentBucket in parentBuckets:
                noChild = True
                for childLat in _lonlatSteps(parentBucket.lat, parentBucket.lonlatRange, lonlatRange):
                    for childLon in _lonlatSteps(parentBucket.lon, parentBucket.lonlatRange, lonlatRange):
                        if (childLat, childLon, parentBucket.time) in bucketsByLatlon:
                            noChild = False
                if noChild:
                    buckets.append(parentBucket)
                else:
                    for childLat in _lonlatSteps(parentBucket.lat, parentBucket.lonlatRange, lonlatRange):
                        for childLon in _lonlatSteps(parentBucket.lon, parentBucket.lonlatRange, lonlatRange):
                            if (childLat, childLon, parentBucket.time) not in bucketsByLatlon:
                                parentBucketCopy = copy.deepcopy(parentBucket)
                                parentBucketCopy.lat = childLat
                                parentBucketCopy.lon = childLon
                                parentBucketCopy.count = None
                                parentBucketCopy.lonlatRange = lonlatRange
                                buckets.append(parentBucketCopy)

        print(f"Combined with parents: {len(buckets)} {'raw' if raw else 'anon'} buckets with range {lonlatRange}.")
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
