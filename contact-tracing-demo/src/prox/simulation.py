import datetime
import random
import copy
from common import WarningCounter
from person import PersonInfo
from place import PlaceInfo


class Simulation:
    @staticmethod
    def generateVisits(startDate, numDays, policy, maxSchedulingIterations=3):
        WarningCounter.reset()
        endDate = startDate + datetime.timedelta(days=numDays-1)
        cutoff = datetime.datetime.combine(endDate, datetime.time(23, 59, 59))
        simulation = Simulation(policy.getPeople())
        simulation._initHome(startDate, endDate)
        date = startDate
        for i in range(numDays):
            simulation._simulateDay(date, policy, cutoff, maxSchedulingIterations)
            date += datetime.timedelta(days=1)
        simulation._mergeAdjacent()
        WarningCounter.print()
        return simulation._obtainVisits()

    @staticmethod
    def mergeVisits(allVisits, visits):
        """
        Merges data in visits with allVisits

        :param allVisits:
        :param visits:
        :return:
        """
        if len(allVisits) == 0:
            allVisits = copy.deepcopy(visits)
        for place, placeVisits in visits.items():
            if place not in allVisits:
                allVisits[place] = placeVisits
            else:
                for visit in placeVisits:
                    allVisits.place.append(visit)

    @staticmethod
    def populateVisitsDb(visits, cur, conn, flush=True):
        """
            Creates a 'visits' table in the database and populates it with visits data
        """
        if flush:
            sql = '''DROP TABLE IF EXISTS visits;'''
            cur.execute(sql)
            sql = '''CREATE TABLE IF NOT EXISTS visits(
                    pid text,
                    place_type text,
                    place_name text,
                    start datetime,
                    end datetime
                );'''
            cur.execute(sql)
        for place, placeVisits in visits.items():
            for visit in placeVisits:
                person = visit[0]
                start = visit[1]
                end = visit[2]
                sql = f'''
                    INSERT INTO visits VALUES(
                        '{person.id_}',
                        '{place.placeName}',
                        '{place.name}',
                        '{start}',
                        '{end}'
                    );
                '''
                cur.execute(sql)
        conn.commit()
        return

    @staticmethod
    def checkBeginEnd(begin, end):
        if end < begin:
            raise ValueError(f"End before begin. Begin: {begin} End: {end}")

    @staticmethod
    def without(beginA, endA, beginB, endB):
        Simulation.checkBeginEnd(beginA, endA)
        Simulation.checkBeginEnd(beginB, endB)
        if beginB <= beginA and endA <= endB:
            return []
        if endA <= beginB or endB <= beginA:
            return [(beginA, endA)]
        if beginA < beginB and endA <= endB:
            return [(beginA, beginB)]
        if beginB <= beginA and endB < endA:
            return [(endB, endA)]
        if beginA < beginB and endB < endA:
            return [(beginA, beginB), (endB, endA)]
        raise RuntimeError(f"Impossible case detected. All cases should have been handled by this point.")

    @staticmethod
    def _scheduleVisits(date, placesToVisit, maxSchedulingIterations, iteration=1):
        visits = []
        for place in placesToVisit:
            beginVisit, endVisit = PlaceInfo.assignVisitTimes(place.placeName, date)
            visits.append((place, beginVisit, endVisit))
        visits = sorted(visits, key=lambda v: v[1])
        overlap = False
        previousVisit = None
        for visit in visits:
            if previousVisit is not None and visit[1] < previousVisit[2]:
                overlap = True
                break
            previousVisit = visit
        if not overlap:
            return visits
        if iteration < maxSchedulingIterations:
            return Simulation._scheduleVisits(date, placesToVisit, maxSchedulingIterations, iteration=iteration + 1)
        WarningCounter.count("Failed to schedule visits in non-overlapping manner. Will return ranked order.")
        rankedVisits = []
        for placeName in PlaceInfo.getRankedPlaceNames():
            for visit in visits:
                if visit[0].placeName == placeName:
                    rankedVisits.append(visit)
        return rankedVisits

    def __init__(self, people):
        self._people = {person: [] for person in people}
        self._places = dict()

    def _overlapping(self, person, begin, end):
        Simulation.checkBeginEnd(begin, end)
        overlapping = []
        for visitPlace, visitBegin, visitEnd in self._people[person]:
            if begin <= visitBegin < end or begin < visitEnd <= end or (visitBegin < begin and end < visitEnd):
                overlapping.append((visitPlace, visitBegin, visitEnd))
        return overlapping

    def _checkExists(self, person, place):
        if place not in self._places:
            self._places[place] = dict()
        if person not in self._places[place]:
            self._places[place][person] = []

    def _remove(self, person, place, begin, end):
        Simulation.checkBeginEnd(begin, end)
        self._checkExists(person, place)
        self._people[person].remove((place, begin, end))
        self._places[place][person].remove((begin, end))

    def _fits(self, person, place, begin, end):
        if self._overlapping(person, begin, end):
            return False
        self._checkExists(person, place)
        for visitBegin, visitEnd in self._places[place][person]:
            if begin <= visitBegin < end or begin < visitEnd <= end or (visitBegin < begin and end < visitEnd):
                raise RuntimeError(f"Peoples' and places' visit lists differ. This should never happen.")
        return True

    def _add(self, person, place, begin, end):
        if not self._fits(person, place, begin, end):
            raise ValueError(f"Visit does not fit.")
        self._people[person].append((place, begin, end))
        self._places[place][person].append((begin, end))

    def _addAdjust(self, person, place, begin, end):
        overlapping = self._overlapping(person, begin, end)
        for visitPlace, visitBegin, visitEnd in overlapping:
            self._remove(person, visitPlace, visitBegin, visitEnd)
            remaining = Simulation.without(visitBegin, visitEnd, begin, end)
            if remaining is None:
                continue
            else:
                for b, e in remaining:
                    self._add(person, visitPlace, b, e)
        self._add(person, place, begin, end)

    def _mergeAdjacent(self):
        for person in self._people:
            tmpVisits = self._people[person].copy()
            previous = None
            for place, begin, end in tmpVisits:
                if previous is not None and previous[0] == place and previous[2] == begin:
                    self._remove(person, place, previous[1], previous[2])
                    self._remove(person, place, begin, end)
                    self._add(person, place, previous[1], end)
                    previous = (place, previous[1], end)
                else:
                    previous = (place, begin, end)

    def _generateHome(self, person, startDate, endDate):
        homeBegin = datetime.datetime.combine(startDate, datetime.time(0, 0, 0))
        homeEnd = datetime.datetime.combine(endDate, datetime.time(23, 59, 59))
        self._add(person, person.home, homeBegin, homeEnd)

    def _generateWork(self, person, date, policy, cutoff):
        if policy.isWorking(person):
            workBegin, workEnd = PlaceInfo.assignWorkTimes(person.work.placeName, date)
            if workEnd > cutoff:
                workEnd = cutoff
            self._addAdjust(person, person.work, workBegin, workEnd)

    def _generateVisits(self, person, date, policy, cutoff, maxSchedulingIterations):
        if not person.visits:
            return
        placesToVisit = []
        for placeName, places in person.favPlaces.items():
            visitRatio = 1.0 / person.visitFreqs[placeName]
            if random.random() < PersonInfo.favRatios[0] * visitRatio and policy.decideVisit(places[0]):
                placesToVisit.append(places[0])
            if random.random() < PersonInfo.favRatios[1] * visitRatio and policy.decideVisit(places[1]):
                placesToVisit.append(places[1])
            randomPlace = random.choice(policy.getPlaces(placeName))
            if random.random() < PersonInfo.favRatios[2] * visitRatio and policy.decideVisit(randomPlace):
                placesToVisit.append(randomPlace)
        visits = Simulation._scheduleVisits(date, placesToVisit, maxSchedulingIterations)
        for visit in visits:
            end = visit[2]
            if end > cutoff:
                end = cutoff
            self._addAdjust(person, visit[0], visit[1], end)

    def _initHome(self, startDate, endDate):
        for person in self._people:
            self._generateHome(person, startDate, endDate)

    def _simulateDay(self, date, policy, cutoff, maxSchedulingIterations):
        for person in self._people:
            self._generateWork(person, date, policy, cutoff)
            self._generateVisits(person, date, policy, cutoff, maxSchedulingIterations)

    def _obtainVisits(self):
        visits = dict()
        for place, peopleDict in self._places.items():
            visits[place] = []
            for person, timesList in peopleDict.items():
                for begin, end in timesList:
                    visits[place].append((person, begin, end))
        return visits
