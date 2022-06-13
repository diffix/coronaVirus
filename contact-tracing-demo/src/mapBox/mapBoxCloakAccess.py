import datetime

from cloakConfig import CloakConfig
from sql_adapter import SQLAdapter


class MapBoxCloakAccess:
    def __init__(self):
        self._sqlAdapter = SQLAdapter(CloakConfig.parameters)

    def queryEncounterBuckets(self, latRange, lonRange, timeRange=None, raw=False):
        sql = f"SELECT diffix.round_by(pickup_latitude, {latRange}) as lat, diffix.round_by(pickup_longitude, {lonRange}) as lon, "
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
            lat = row[0]
            lon = row[1]
            # time = None
            time = datetime.datetime.fromtimestamp(0)
            if 3 < len(row):
                time = row[2]
            if lat is None or lon is None or (3 < len(row) and time is None):
                filtered += 1
                continue
            buckets.append(MapBoxBucket(lat, lon, time=time, count=row[len(row) - 1]))
        print(f"Loaded {len(result)} buckets from cloak.")
        print(f"Filtered {filtered} buckets due to */NULL values.")
        self._sqlAdapter.disconnect()
        return buckets


class MapBoxBucket:
    def __init__(self, lat, lon, time=None, count=-1):
        self.lat = lat
        self.lon = lon
        self.time = time
        self.count = count

    def __str__(self):
        return f"MapBoxEncounters: {self.listOfStrings()}"

    __repr__ = __str__

    def listOfStrings(self):
        return [f"{v}" for v in [self.lat, self.lon, self.time, self.count] if v is not None]
