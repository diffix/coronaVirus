import random
import uuid
from common import Gender
from place import PlaceInfo, Place, PlaceCapacityTracker


class PersonInfo:
    ages = {
        'childMin': 0,  # inclusive
        'childMax': 20,  # exclusive
        'adultMin': 20,  # inclusive
        'adultMax': 90,  # exclusive
        'schoolMin': 5,  # inclusive
        'schoolMax': 20,  # exclusive
        'workMin': 20,  # inclusive
        'workMax': 60,  # exclusive
        'visitMin': 8,  # inclusive
        'visitMax': 80,  # exclusive
        'atRiskLow': 4,  # exclusive!!!
        'atRiskHigh': 65,  # inclusive!!!
    }

    """
    Gender distribution in Kaiserslautern:
    | total | female | male  |
    | ----- | ------ | ----- |
    | 96340 | 48638  | 47703 |
    | 100   | 50.5   | 49.5  |
    """
    genderRatios = [0.50, 0.49, 0.01]  # FEMALE=49.5% MALE=49.5% OTHER=1%
    workRatio = 0.8  # 80% working 20% non-working (stay at home)
    favRatios = [4/7, 2/7, 1/7]  # fav1 = 2*fav2, fav2 = 2*rand, rand
    atRiskRatio = 0.05  # 5% of people within 'atRiskLow' and 'atRiskHigh'

    @staticmethod
    def hasChildAge(age):
        return PersonInfo.ages['childMin'] <= age < PersonInfo.ages['childMax']

    @staticmethod
    def hasAdultAge(age):
        return PersonInfo.ages['adultMin'] <= age < PersonInfo.ages['adultMax']

    @staticmethod
    def hasSchoolAge(age):
        return PersonInfo.ages['schoolMin'] <= age < PersonInfo.ages['schoolMax']

    @staticmethod
    def hasWorkAge(age):
        return PersonInfo.ages['workMin'] <= age < PersonInfo.ages['workMax']

    @staticmethod
    def hasVisitAge(age):
        return PersonInfo.ages['visitMin'] <= age < PersonInfo.ages['visitMax']

    @staticmethod
    def assignAge():
        return random.randrange(PersonInfo.ages['childMin'], PersonInfo.ages['adultMax'])

    @staticmethod
    def assignChildAge():
        return random.randrange(PersonInfo.ages['childMin'], PersonInfo.ages['childMax'])

    @staticmethod
    def assignAdultAge():
        return random.randrange(PersonInfo.ages['adultMin'], PersonInfo.ages['adultMax'])

    @staticmethod
    def assignGender():
        return random.choices(list(Gender), weights=PersonInfo.genderRatios, k=1)[0]

    @staticmethod
    def assignWorks(age):
        if PersonInfo.hasSchoolAge(age) or (PersonInfo.hasWorkAge(age) and random.random() < PersonInfo.workRatio):
            return True
        else:
            return False

    @staticmethod
    def assignVisits(age):
        return PersonInfo.hasVisitAge(age)

    @staticmethod
    def assignAtRisk(age):
        if age < PersonInfo.ages['atRiskLow'] or PersonInfo.ages['atRiskHigh'] <= age or \
                random.random() < PersonInfo.atRiskRatio:
            return True
        return False


class Person:
    """
    holds demographic info about each person
    """
    @staticmethod
    def _generatePerson(home, id_=None, age=None, gender=None, atRisk=None, works=None, visits=None, work=None,
                        visitFreqs=None, favPlaces=None):
        id_ = str(uuid.uuid4()) if id_ is None else id_
        age = PersonInfo.assignAge() if age is None else age
        gender = PersonInfo.assignGender() if gender is None else gender
        atRisk = PersonInfo.assignAtRisk(age) if atRisk is None else atRisk
        works = PersonInfo.assignWorks(age) if works is None else works
        visits = PersonInfo.assignVisits(age) if visits is None else visits
        visitFreqs = PlaceInfo.assignVisitFreqs() if visitFreqs is None else visitFreqs
        return Person(id_, age, gender, atRisk, works, visits, home, work=work, visitFreqs=visitFreqs,
                      favPlaces=favPlaces)

    @staticmethod
    def generatePeople(homes):
        """
        Generates list of people according to their homes and assign each person's home.
        :param homes: dict
        in format of {homeType: [Place(..."home"...), Place(..."home"...), ...]}
        :return: list
        list of person objects according to age distribution and homes capacities with their homes assigned

        ## usage/test
        >>> homes = Place.generateHomes(numPeople=1000)
        >>> len(homes.keys()) == len(PlaceInfo.homeTypes.keys())
        True
        >>> totalCap = 0
        >>> for homeType, lstHomes in homes.items(): \
                totalCap += ((homeType[0] + homeType[1]) * len(lstHomes))
        >>> people = Person.generatePeople(homes)
        >>> len(people) == totalCap
        True
        """
        people = list()
        for homeType, lstHomes in homes.items():
            for home in lstHomes:
                for _ in range(homeType[0]):
                    people.append(Person._generatePerson(home, age=PersonInfo.assignAdultAge()))
                for _ in range(homeType[1]):
                    people.append(Person._generatePerson(home, age=PersonInfo.assignChildAge()))
        return people

    @staticmethod
    def getTableIndices():
        return {"pid":0,"age":1,"gender":2,"at_risk":3,"role":4,"home":5,"work":6}

    @staticmethod
    def populatePeopleDb(people, cur, conn):
        """
            Creates a 'people' table in the database and populates it with people data
        """
        sql = '''DROP TABLE IF EXISTS people;'''
        cur.execute(sql)
        sql = '''CREATE TABLE IF NOT EXISTS people(
                id text,
                age int,
                gender text,
                at_risk int,
                role text,
                home text,
                work text,
            '''
        for place in PlaceInfo.getPlaceNames():
            sql += place + '_visit_freq int, '
        for place in PlaceInfo.getPlaceNames():
            sql += place + '_first_fav text, '
            sql += place + '_second_fav text, '
        sql = sql[:-2]
        sql += ');'
        cur.execute(sql)
        for person in people:
            sql = f'''
                INSERT INTO people VALUES(
                    '{person.id_}',
                    {person.age},
                    '{person.gender}',
                    '{1 if person.atRisk else 0}',
                    '{'home' if person.work is None else 'student' if person.work.name.startswith('school') else 
                        'worker'}',
                    '{person.home.name}',
                    '{person.work.name if person.work is not None else ""}', 
            '''
            for place in PlaceInfo.getPlaceNames():
                sql += f"{person.visitFreqs[place] if person.visitFreqs is not None else -1}, "
            for place in PlaceInfo.getPlaceNames():
                sql += f"'{person.favPlaces[place][0].name if person.favPlaces is not None else ''}', "
                sql += f"'{person.favPlaces[place][1].name if person.favPlaces is not None else ''}', "
            sql = sql[:-2]
            sql += ');'
            cur.execute(sql)
        conn.commit()
        return

    @staticmethod
    def _assignWork(people, places):
        randomizedPlaces = random.sample(places, len(places))
        count = 0
        tracker = PlaceCapacityTracker()
        for person in people:
            while not tracker.hasWorkCapacity(randomizedPlaces[count % len(randomizedPlaces)]):
                del randomizedPlaces[count % len(randomizedPlaces)]
            tracker.useWorkCapacity(randomizedPlaces[count % len(randomizedPlaces)])
            person.work = randomizedPlaces[count % len(randomizedPlaces)]
            count += 1

    @staticmethod
    def assignWorkPlaces(people, workPlaces):
        pupils = [p for p in people if p.works and PersonInfo.hasSchoolAge(p.age)]
        nonPupils = [p for p in people if p.works and not PersonInfo.hasSchoolAge(p.age)]
        schools = workPlaces['school']
        nonSchools = list()
        for placeType, places in workPlaces.items():
            if placeType != 'school':
                nonSchools.extend(places)
        Person._assignWork(pupils, schools)
        Person._assignWork(nonPupils, nonSchools)

    @staticmethod
    def _choose(places, count, tracker, requiredCapacity, doNotChoose):
        skipped = 0
        while True:
            if not tracker.hasVisitCapacity(places[count % len(places)]):
                del places[count % len(places)]
            elif not tracker.hasVisitCapacityFor(places[count % len(places)], requiredCapacity):
                count += 1
                skipped += 1
                if skipped >= len(places):
                    break
            else:
                place = places[count % len(places)]
                count += 1
                if place == doNotChoose and len(places) > 1:
                    continue
                tracker.useVisitCapacity(place, requiredCapacity)
                return place, count
        sortedList = sorted(places, key=lambda p: tracker.remainingVisitCapacity(p), reverse=True)
        place = sortedList[0]
        if place == doNotChoose and len(sortedList) > 1:
            place = sortedList[1]
        tracker.useVisitCapacity(place, requiredCapacity, force=True)
        return place, count

    @staticmethod
    def assignFavorites(people, workPlaces, homes):
        visitors = [p for p in people if p.visits]
        allHomes = list()
        for homeType, homesLst in homes.items():
            allHomes.extend(homesLst)
        places = workPlaces.copy()
        places['home'] = allHomes
        for placeName in places.keys():
            places[placeName] = random.sample(places[placeName], len(places[placeName]))
        count = 0
        tracker = PlaceCapacityTracker()
        for person in visitors:
            person.favPlaces = dict()
            for placeName, visitFreq in person.visitFreqs.items():
                visitRatio = 1.0 / visitFreq
                fav0, count = Person._choose(places[placeName], count, tracker, PersonInfo.favRatios[0] * visitRatio,
                                             person.home if placeName == 'home' else person.work)
                fav1, count = Person._choose(places[placeName], count, tracker, PersonInfo.favRatios[1] * visitRatio,
                                             person.home if placeName == 'home' else person.work)
                person.favPlaces[placeName] = (fav0, fav1)

    def __init__(self, id_, age, gender, atRisk, works, visits, home, work=None, visitFreqs=None, favPlaces=None):
        self.id_ = id_
        self.age = age
        self.gender = gender
        self.atRisk = atRisk
        self.works = works
        self.visits = visits
        self.home = home
        self.work = work
        self.visitFreqs = visitFreqs
        self.favPlaces = favPlaces

    def __str__(self):
        rStr = str(f"<Person\n"
                   f"    id={self.id_}\n"
                   f"    age={self.age}\n"
                   f"    gender={self.gender}\n"
                   f"    atRisk={self.atRisk}\n"
                   f"    works={self.works}\n"
                   f"    visits={self.visits}\n"
                   f"    home={self.home.name}\n"
                   f"    work={self.work.name if self.work is not None else None}\n"
                   f"    visitFreqs={self.visitFreqs}\n"
                   f"    favPlaces=")
        if self.favPlaces is not None:
            for placeName, tup in self.favPlaces.items():
                rStr += str(f"({tup[0].name}, {tup[1].name}), ")
            rStr = rStr[:-2]
        else:
            rStr += "None"
        rStr += '>\n'
        return rStr
    __repr__ = __str__

    def hasSchoolAge(self):
        return PersonInfo.hasSchoolAge(self.age)


if __name__ == '__main__':
    pass
