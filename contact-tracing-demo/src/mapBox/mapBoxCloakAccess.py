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

def _hasChild(startLat, startLon, parentRange, parentTime, childRange, bucketsByLatlon):
    for childLat in _lonlatSteps(startLat, parentRange, childRange):
        for childLon in _lonlatSteps(startLon, parentRange, childRange):
            if (childLat, childLon, parentTime) in bucketsByLatlon:
                return True
    return False

def _copyAndSetLonlat(bucket, lat, lon, lonlatRange):
    parentBucketCopy = copy.deepcopy(bucket)
    parentBucketCopy.lat = lat
    parentBucketCopy.lon = lon
    parentBucketCopy.count = None
    parentBucketCopy.lonlatRange = lonlatRange
    return parentBucketCopy



def _appendParentBucket(parentBucket, lonlatRange, buckets, bucketsByLatlon):

    noChild = not _hasChild(parentBucket.lat, parentBucket.lon, parentBucket.lonlatRange, parentBucket.time, lonlatRange, bucketsByLatlon)
    if noChild:
        # at this level, the parent has no children whatsoever - we plant the parent and we're done
        buckets.append(parentBucket)
        bucketsByLatlon[(parentBucket.lat, parentBucket.lon, parentBucket.time)] = True
    else:
        # parentBuckets might include "grandparents" of the current generation. In such cases, we still might use the intermediate
        # generations, in case where current generation doesn't appear in the intermediate generation level tiles.
        if parentBucket.lonlatRange > lonlatRange * 2:
            # before we use the children from the current level, let's try an intermediate level
            # First, split the parent into immediate children:
            immediateChildLonlatRange = parentBucket.lonlatRange / 2
            immediateChildren = [_copyAndSetLonlat(parentBucket, lat, lon, immediateChildLonlatRange) for lat, lon in
                                [(parentBucket.lat, parentBucket.lon),
                                (parentBucket.lat + immediateChildLonlatRange, parentBucket.lon),
                                (parentBucket.lat, parentBucket.lon + immediateChildLonlatRange),
                                (parentBucket.lat + immediateChildLonlatRange, parentBucket.lon + immediateChildLonlatRange)]]
            for immediateChild in immediateChildren:
                _appendParentBucket(immediateChild, lonlatRange, buckets, bucketsByLatlon)
        else:
            # finally we handle at the level of the "finest" ancestors
            for childLat in _lonlatSteps(parentBucket.lat, parentBucket.lonlatRange, lonlatRange):
                for childLon in _lonlatSteps(parentBucket.lon, parentBucket.lonlatRange, lonlatRange):
                    if (childLat, childLon, parentBucket.time) not in bucketsByLatlon:
                        parentBucketCopy = _copyAndSetLonlat(parentBucket, childLat, childLon, lonlatRange)
                        buckets.append(parentBucketCopy)
                        bucketsByLatlon[(childLat, childLon, parentBucketCopy.time)] = True


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
                _appendParentBucket(parentBucket, lonlatRange, buckets, bucketsByLatlon)

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
