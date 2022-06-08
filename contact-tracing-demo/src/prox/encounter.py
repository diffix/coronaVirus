import random
from place import PlaceInfo
from datetime import datetime, timedelta


class Encounter:
    locErr = 0.00005

    @staticmethod
    def modify(latOrLon):
        return latOrLon + (random.random() * Encounter.locErr) - Encounter.locErr / 2

    @staticmethod
    def getTableIndices():
        return {"pid1":0,"pid2":1,"place_name":2,"place_type":3,"lat":4,"lon":5,"time":6}

    @staticmethod
    def populateEncountersDb(encounters, cur, conn, flush=True):
        """
            Creates an 'encounters' table in the database and populates it
        """
        if flush:
            sql = '''DROP TABLE IF EXISTS encounters;'''
            cur.execute(sql)
            sql = '''CREATE TABLE IF NOT EXISTS encounters(
                    pid1 text,
                    pid2 text,
                    place_name text,
                    place_type text,
                    lat real,
                    lon real,
                    time datetime
                );'''
            cur.execute(sql)
        for encounter in encounters:
            sql = f'''
                INSERT INTO encounters VALUES(
                    '{encounter['person1'].id_}',
                    '{encounter['person2'].id_}',
                    '{encounter['place'].name}',
                    '{encounter['place'].placeName}',
                    {Encounter.modify(encounter['place'].lat)},
                    {Encounter.modify(encounter['place'].lon)},
                    '{encounter['time']}'
                );
            '''
            cur.execute(sql)
        conn.commit()
        return

    @staticmethod
    def addToDistinct(dp, p, cnt):
        if p not in dp:
            dp[p] = 1
            return cnt + 1
        else:
            # Shouldn't get here unless visits overlap for a given user
            dp[p] += 1
            return cnt

    @staticmethod
    def rmFromDistinct(dp, p, cnt):
        dp[p] -= 1
        if dp[p] == 0:
            del dp[p]
            return cnt - 1
        # Shouldn't get here unless visits overlap for a given user
        return cnt

    @staticmethod
    def makeEncountersFromVisits(place, visits):
        """
            visits is a list of [person,startTime,endTime] tuples
            startTime and endTime are python datetime types
            placeType is one of 'office', 'school', etc.
    
            Method: First pass, go through and determine expected number
                of encounters for each person based on how many person
                seconds of overlap that exists for that person.
              * Second pass, assign that number of encounters randomly
    
            Returns: list of encounters as:
                [{'place':place, 'person1':person1,'person2':person2,'time':datetime}, ... ]
        """
        p = 0
        st = 1
        et = 2
        encounters = []
        # encHrPer is probability of encountering a person given one hour
        # of being in the same place.
        encHrPer = PlaceInfo.getEncounterRate(place.placeName)
        dtMinStart = datetime.fromisoformat('2100-01-01 10:00:00')
        # Determine the min start time
        for visit in visits:
            if visit[st] < dtMinStart:
                dtMinStart = visit[st]
        if dtMinStart.hour <= 5:
            # This is a home visit in the middle of the night
            homeVisit = True
        else:
            homeVisit = False
        # We want to compute the total person-pair seconds. From this we'll
        # determine how many encounters to assign
        events = []
        # endTimes = []
        # Record the startTimes and endTimes as seconds since minimum start time
        # Record also the person associated with the time
        for visit in visits:
            tdelElapsed = visit[st] - dtMinStart
            elapsed = int(tdelElapsed.total_seconds())
            events.append([elapsed, 'start', visit[p]])
            tdelElapsed = visit[et] - dtMinStart
            elapsed = int(tdelElapsed.total_seconds())
            events.append([elapsed, 'end', visit[p]])
        events.sort(key=lambda t: t[0])
        distinctPersons = {}
        total = 0
        numPersons = 0
        for i in range(len(events)):
            if events[i][1] == 'start':
                numPersons = Encounter.addToDistinct(distinctPersons, events[i][2], numPersons)
            else:
                numPersons = Encounter.rmFromDistinct(distinctPersons, events[i][2], numPersons)
            if i == len(events) - 1:
                break
            total += numPersons * (numPersons - 1) * (events[i+1][0] - events[i][0])
        # print(f"total person-pair seconds = {total}")
        totalEncounters = int(encHrPer * (total / 3600))
        # print(f"total encounters = {totalEncounters}")
        # Assign a time to each encounter. Assigned within a gaussian dist.
        if len(events) < 7:
            minElapsedSec = events[0][0]
            maxElapsedSec = events[len(events)-1][0]
            elapsedRange = maxElapsedSec - minElapsedSec
        else:
            minElapsedSec = events[2][0]
            maxElapsedSec = events[len(events)-3][0]
            elapsedRange = maxElapsedSec - minElapsedSec
        if elapsedRange <= 5:
            minElapsedSec = events[0][0]
            maxElapsedSec = events[len(events)-1][0]
            elapsedRange = maxElapsedSec - minElapsedSec
        sd = elapsedRange / 5
        mean = minElapsedSec + (elapsedRange/2)
        elapsedSecs = []
        for _ in range(totalEncounters):
            # pick a number of elapsed seconds
            cnt = 0
            while True:
                cnt += 1
                if cnt > 1000:
                    print(minElapsedSec, maxElapsedSec)
                    print(totalEncounters)
                    print(events)
                    quit()
                eventSec = int(random.gauss(mean, sd))
                if minElapsedSec < eventSec < maxElapsedSec:
                    break
            # This is a hack, but I don't want so many encounters at night when people
            # are sleeping at home.
            if homeVisit and eventSec < 18000:
                # This is a night visit before 5AM or so. Reduce probability of an encounter
                if random.random() < 0.1:
                    elapsedSecs.append(eventSec)
            else:
                elapsedSecs.append(eventSec)
        elapsedSecs.sort()
        # At this point, elapsedSecs contains a list of encounter times as
        # offsets from the first event time in seconds, sorted
        # events contains a list of start/end events and associated person, sorted
        # What I'm going to do is go through the events and keep a list of persons
        # who are present at any point in time. Then I'll assign randomly
        # from this list
        ei = 0
        distinctPersons = {}
        for event in events:
            if ei >= len(elapsedSecs):
                break
            # eventTime = dtMinStart + timedelta(seconds=event[0])
            # encounterTime = dtMinStart + timedelta(seconds=elapsedSecs[ei])
            # print(f"{eventTime}, {event[0]}, {event[1]}, {event[2].pid} ... (encounter: {encounterTime})")
            if event[1] == 'start':
                Encounter.addToDistinct(distinctPersons, event[2], numPersons)
            else:
                Encounter.rmFromDistinct(distinctPersons, event[2], numPersons)
            persons = []
            for per in distinctPersons.keys():
                persons.append(per)
            # print(persons)
            if event[0] > elapsedSecs[ei]:
                # Assign this encounter to two random persons
                persons = list(distinctPersons.keys())
                if len(persons) <= 1:
                    # can't assign a pair, so just skip it
                    ei += 1
                    continue
                # assign the datetime to the elapsed seconds
                dtEventTime = dtMinStart + timedelta(seconds=elapsedSecs[ei])
                ei += 1
                # pick a pair of persons
                person1 = random.choice(persons)
                # print(f"Try {ei}, {len(persons)} people")
                while True:
                    person2 = random.choice(persons)
                    if person1 == person2:
                        continue
                    break
                encounters.append({'place': place, 'person1': person1, 'person2': person2, 'time': dtEventTime})
        return encounters

    @staticmethod
    def generateEncountersDay(allVisits):
        allEncounters = []
        for place, placeVisits in allVisits.items():
            encounters = Encounter.makeEncountersFromVisits(place, placeVisits)
            for encounter in encounters:
                allEncounters.append(encounter)
        return allEncounters


if __name__ == '__main__':
    pass

