import datetime
import random


class Aggregator:
    @staticmethod
    def _aggregateNumeric(encounters, begin, delta, accessFunction, setFunction, randomFunction, people=None):
        tmpBegin = begin
        encounters.sort(key=lambda ea: accessFunction(ea[0], people))
        for e, a in encounters:
            if accessFunction(e, people) < tmpBegin:
                continue
            while tmpBegin + delta <= accessFunction(e, people):
                tmpBegin += delta
            setFunction(a, randomFunction(tmpBegin, delta))
        return begin, delta, accessFunction

    @staticmethod
    def _bucketize(encounters, bucketizations, people=None):
        buckets = dict()
        for e, a in encounters:
            finalDct = buckets
            for b in bucketizations:
                begin = b[0]
                delta = b[1]
                accessFunction = b[2]
                if accessFunction(e, people) < begin:
                    break
                while begin + delta <= accessFunction(e, people):
                    begin += delta
                if begin not in finalDct:
                    finalDct[begin] = dict()
                finalDct = finalDct[begin]
            else:
                if e.pid1 not in finalDct:
                    finalDct[e.pid1] = list()
                finalDct[e.pid1].append((e, a))
        return buckets

    @staticmethod
    def _printStats(stats):
        total = [0, 0, 0, 0]
        perBucketization = dict()
        distinct = dict()
        for stat in stats:
            isFiltered = stat[len(stat) - 1]
            numEnc = stat[len(stat) - 2]
            numDistinct = stat[len(stat) - 3]
            total[0] += 1
            total[1] += numEnc
            if isFiltered:
                total[2] += 1
                total[3] += numEnc
            for i in range(len(stat) - 3):
                if i not in perBucketization:
                    perBucketization[i] = dict()
                if stat[i] not in perBucketization[i]:
                    perBucketization[i][stat[i]] = [0, 0, 0, 0]
                perBucketization[i][stat[i]][0] += 1
                perBucketization[i][stat[i]][1] += numEnc
                if isFiltered:
                    perBucketization[i][stat[i]][2] += 1
                    perBucketization[i][stat[i]][3] += numEnc
            if numDistinct not in distinct:
                distinct[numDistinct] = [0, 0]
            distinct[numDistinct][0] += 1
            if isFiltered:
                distinct[numDistinct][1] += 1
        print(f"|    Filtered {total[2]} ({total[2] / total[0] * 100:.1f}%) of {total[0]} buckets "
              f"and {total[3]} ({total[3] / total[1] * 100:.1f}%) of {total[1]} encounters.")
        for i, dimDct in perBucketization.items():
            print(f"|    Dimension {i + 1}")
            print(f"|       Total t and filtered f buckets per range r --> (r, t, f, %):")
            bs = sorted([(r, v[0], v[2], round(v[2] / v[0] * 100, 1)) for r, v in dimDct.items()], key=lambda j: j[0])
            for b in bs:
                print(f"|          {b}")
            print(f"|       Total t and filtered f encounters per range r --> (r, t, f, %):")
            es = sorted([(r, v[1], v[3], round(v[3] / v[1] * 100, 1)) for r, v in dimDct.items()], key=lambda j: j[0])
            for e in es:
                print(f"|          {e}")
        print(f"|    How many buckets (total t, filtered f) have d distinct pids? --> [(d, t, f)]:")
        ds = sorted([(d, v[0], v[1]) for d, v in distinct.items()], key=lambda j: j[0])
        for d in ds:
            print(f"|       {d}")

    @staticmethod
    def lowCount(encounters, bucketizations, minDistinct, people=None):
        buckets = Aggregator._bucketize(encounters, bucketizations, people=people)
        result = list()
        stats = list()
        while buckets:
            finalDct = buckets
            stat = []
            for _ in bucketizations:
                nextDct = None
                vToDel = []
                for v, d in finalDct.items():
                    if not d:
                        vToDel.append(v)
                    else:
                        nextDct = d
                        stat.append(v)
                        break
                for v in vToDel:
                    del finalDct[v]
                if nextDct is None:
                    break
                else:
                    finalDct = nextDct
            else:
                stat.append(len(finalDct.keys()))
                numEnc = 0
                for lst in finalDct.values():
                    numEnc += len(lst)
                stat.append(numEnc)
                if minDistinct <= len(finalDct.keys()):
                    stat.append(False)
                    for lst in finalDct.values():
                        result.extend(lst)
                else:
                    stat.append(True)
                stats.append(stat)
                finalDct.clear()
        Aggregator._printStats(stats)
        return result

    @staticmethod
    def _setTime(aggregatedEncounter, time):
        aggregatedEncounter.time = time

    @staticmethod
    def aggregateTime(encounters, begin, delta):
        return [Aggregator._aggregateNumeric(encounters, begin, delta, lambda e, p: e.time, Aggregator._setTime,
                                             lambda b, d: b + datetime.timedelta(
                                                seconds=round(random.random() * d.total_seconds())))]

    @staticmethod
    def _setLat(aggregatedEncounter, lat):
        aggregatedEncounter.lat = lat

    @staticmethod
    def _setLon(aggregatedEncounter, lon):
        aggregatedEncounter.lon = lon

    @staticmethod
    def aggregateLocation(encounters, latBegin, latDelta, lonBegin, lonDelta):
        return [Aggregator._aggregateNumeric(encounters, latBegin, latDelta, lambda e, p: e.lat, Aggregator._setLat,
                                             lambda b, d: round(b + random.random() * d, 6)),
                Aggregator._aggregateNumeric(encounters, lonBegin, lonDelta, lambda e, p: e.lon, Aggregator._setLon,
                                             lambda b, d: round(b + random.random() * d, 6))]

    @staticmethod
    def _setPlaceType(aggregatedEncounter, placeType):
        aggregatedEncounter.placeType = placeType

    @staticmethod
    def aggregatePlaceType(encounters):
        tracker = EnumTracker()
        return [Aggregator._aggregateNumeric(encounters, 0, 1, lambda e, p: tracker.getIndex(e.placeType),
                                             Aggregator._setPlaceType, lambda b, d: b)]

    @staticmethod
    def _setAge(aggregatedEncounter, age):
        aggregatedEncounter.age = age

    @staticmethod
    def aggregateAge(encounters, people, begin, delta):
        return [Aggregator._aggregateNumeric(encounters, begin, delta, lambda e, p: p[e.pid1].age, Aggregator._setAge,
                                             lambda b, d: int(b + random.random() * d), people=people)]

    @staticmethod
    def _setGender(aggregatedEncounter, gender):
        aggregatedEncounter.gender = gender

    @staticmethod
    def aggregateGender(encounters, people):
        tracker = EnumTracker()
        return [Aggregator._aggregateNumeric(encounters, 0, 1, lambda e, p: tracker.getIndex(p[e.pid1].gender),
                                             Aggregator._setGender, lambda b, d: b, people=people)]

    @staticmethod
    def _setAtRisk(aggregatedEncounter, atRisk):
        aggregatedEncounter.atRisk = atRisk

    @staticmethod
    def aggregateAtRisk(encounters, people):
        return [Aggregator._aggregateNumeric(encounters, 0, 1, lambda e, p: p[e.pid1].atRisk, Aggregator._setAtRisk,
                                             lambda b, d: b, people=people)]

    @staticmethod
    def _setRole(aggregatedEncounter, role):
        aggregatedEncounter.role = role

    @staticmethod
    def aggregateRole(encounters, people):
        tracker = EnumTracker()
        return [Aggregator._aggregateNumeric(encounters, 0, 1, lambda e, p: tracker.getIndex(p[e.pid1].role),
                                             Aggregator._setRole, lambda b, d: b, people=people)]


class EnumTracker:
    def __init__(self):
        self._dct = dict()
        self._index = 0

    def getIndex(self, value):
        if value not in self._dct:
            print(f"|       Dimension value mapping: {value} --> {self._index}")
            self._dct[value] = self._index
            self._index += 1
        return self._dct[value]
