import datetime
import json
import random
from common import WarningCounter


class PlaceInfo:
    """
    """
    placeTypes = {
        'home': {
            'work': {
                'minCapacity': 1,
                'maxCapacity': 6,
                'minArrive': None,
                'maxArrive': None,
                'minLengthMin': None,
                'maxLengthMin': None,
                'open': 1.0,
                'happening': 1.0,
            },
            'visit': {
                'minCapacity': 1,
                'maxCapacity': 10,
                'minArrive': '10:00:00',
                'maxArrive': '21:00:00',
                'minLengthMin': 5,
                'maxLengthMin': 480,
                'avgOccupancy': 1.0,
                'lowFreqDay': 30,
                'highFreqDay': 10,
                'open': 1.0,
                'happening': 1.0,
            },
            'encountersPerPairPerHour': 0.1,
            'rank': 0
        },
        'school': {
            'work': {
                'minCapacity': 20,
                'maxCapacity': 150,
                'minArrive': '08:00:00',
                'maxArrive': '09:00:00',
                'minLengthMin': 360,
                'maxLengthMin': 480,
                'open': 1.0,
                'happening': 1.0,
            },
            'visit': {
                'minCapacity': 10,
                'maxCapacity': 100,
                'minArrive': '10:00:00',
                'maxArrive': '14:00:00',
                'minLengthMin': 5,
                'maxLengthMin': 60,
                'avgOccupancy': 1.0,
                'lowFreqDay': 30,
                'highFreqDay': 15,
                'open': 1.0,
                'happening': 1.0,
            },
            'encountersPerPairPerHour': 0.05,
            'rank': 1
        },
        'office': {
            'work': {
                'minCapacity': 20,
                'maxCapacity': 200,
                'minArrive': '08:00:00',
                'maxArrive': '10:00:00',
                'minLengthMin': 360,
                'maxLengthMin': 480,
                'open': 1.0,
                'happening': 1.0,
            },
            'visit': {
                'minCapacity': 2,
                'maxCapacity': 10,
                'minArrive': '09:00:00',
                'maxArrive': '16:00:00',
                'minLengthMin': 5,
                'maxLengthMin': 120,
                'avgOccupancy': 1.0,
                'lowFreqDay': 30,
                'highFreqDay': 3,
                'open': 1.0,
                'happening': 1.0,
            },
            'encountersPerPairPerHour': 0.05,
            'rank': 2
        },
        'sport': {
            'work': {
                'minCapacity': 3,
                'maxCapacity': 6,
                'minArrive': '08:00:00',
                'maxArrive': '12:00:00',
                'minLengthMin': 360,
                'maxLengthMin': 480,
                'open': 1.0,
                'happening': 1.0,
            },
            'visit': {
                'minCapacity': 10,
                'maxCapacity': 50,
                'minArrive': '09:00:00',
                'maxArrive': '20:00:00',
                'minLengthMin': 30,
                'maxLengthMin': 60,
                'avgOccupancy': 0.2,
                'lowFreqDay': 5,
                'highFreqDay': 1,
                'open': 1.0,
                'happening': 1.0,
            },
            'encountersPerPairPerHour': 0.1,
            'rank': 3
        },
        'super': {
            'work': {
                'minCapacity': 10,
                'maxCapacity': 40,
                'minArrive': '08:00:00',
                'maxArrive': '12:00:00',
                'minLengthMin': 360,
                'maxLengthMin': 480,
                'open': 1.0,
                'happening': 1.0,
            },
            'visit': {
                'minCapacity': 50,
                'maxCapacity': 550,
                'minArrive': '09:00:00',
                'maxArrive': '19:00:00',
                'minLengthMin': 10,
                'maxLengthMin': 90,
                'avgOccupancy': 0.25,
                'lowFreqDay': 7,
                'highFreqDay': 1,
                'open': 1.0,
                'happening': 1.0,
            },
            'encountersPerPairPerHour': 0.1,
            'rank': 4
        },
        'store': {
            'work': {
                'minCapacity': 2,
                'maxCapacity': 10,
                'minArrive': '08:00:00',
                'maxArrive': '10:00:00',
                'minLengthMin': 360,
                'maxLengthMin': 480,
                'open': 1.0,
                'happening': 1.0,
            },
            'visit': {
                'minCapacity': 8,
                'maxCapacity': 80,
                'minArrive': '10:00:00',
                'maxArrive': '17:00:00',
                'minLengthMin': 5,
                'maxLengthMin': 90,
                'avgOccupancy': 0.1,
                'lowFreqDay': 7,
                'highFreqDay': 1,
                'open': 1.0,
                'happening': 1.0,
            },
            'encountersPerPairPerHour': 0.1,
            'rank': 5
        },
        'restaurant': {
            'work': {
                'minCapacity': 2,
                'maxCapacity': 20,
                'minArrive': '11:00:00',
                'maxArrive': '12:00:00',
                'minLengthMin': 360,
                'maxLengthMin': 480,
                'open': 1.0,
                'happening': 1.0,
            },
            'visit': {
                'minCapacity': 5,
                'maxCapacity': 50,
                'minArrive': '12:00:00',
                'maxArrive': '20:00:00',
                'minLengthMin': 30,
                'maxLengthMin': 90,
                'avgOccupancy': 0.15,
                'lowFreqDay': 14,
                'highFreqDay': 1,
                'open': 1.0,
                'happening': 1.0,
            },
            'encountersPerPairPerHour': 0.05,
            'rank': 6
        },
    }

    """
    Households in Kaiserslautern:
    | total | single | couple no kids | couple with kids | single parents | others |
    | ----- | ------ | -------------- | ---------------- | -------------- | ------ |
    | 50816 | 23910  | 12187          | 8828             | 4040           | 1851   |
    | 100   | 47     | 24             | 17.4             | 8              | 3.6    |
    """
    homeTypes = {
        (1, 0): 0.47,  # single
        (1, 1): 0.07,  # single parents a
        (1, 2): 0.01,  # single parents b
        (2, 0): 0.24,  # couple no kids
        (2, 1): 0.10,  # couple with kids a
        (2, 2): 0.05,  # couple with kids b
        (2, 3): 0.02,  # couple with kids c
        (2, 4): 0.004,  # couple with kids d
        (3, 0): 0.03,  # others a
        (3, 1): 0.005,  # others b
        (3, 2): 0.001,  # others c
    }

    """
    Num apartments per building in Kaiserslautern:
    | total | 1 apt | 2 apt | 3-6 apt | 7-12 apt | 13+ apt |
    | ----- | ----- | ----- | ------- | -------- | ------- |
    | 20302 | 11115 | 3456  | 3983    | 1336     | 412     |
    | 100   | 54.8  | 17    | 19.6    | 6.6      | 2       |
    
    We adjust the numbers as there is more addresses than houses, which means the same house has multiple addresses.
    """
    houseTypes = {
        1: 54.8 / 2,
        2: 17 * 2,
        3: 19.6 * 2,
        7: 6.6 * 1.5,
        13: 2 * 1.5,
    }

    storeTypes = {
        'store': 283,
        'clothes': 87,
        'hairdresser': 51,
        'bakery': 30,
        'beauty': 28,
        'kiosk': 27,
        'car': 18,
        'jewelry': 17,
        'mobile_phone': 15,
        'car_repair': 13,
        'travel_agency': 13,
        'furniture': 13,
        'shoes': 13,
        'optician': 13,
        'convenience': 12,
        'florist': 11,
        'butcher': 10,
        'electronics': 10,
        'gift': 9,
        'variety_store': 8,
        'beverages': 7,
    }

    @staticmethod
    def getPlaceNames():
        """ Returns list of place types names
        """
        pn = set(list(PlaceInfo.placeTypes.keys()))
        for st in PlaceInfo.storeTypes.keys():
            n = st
            if st != 'store':
                n = 'store_' + st
            pn.add(n)
        return list(pn)

    @staticmethod
    def getEncounterRate(placeName):
        if placeName.startswith('store_'):
            placeName = 'store'
        return PlaceInfo.placeTypes[placeName]['encountersPerPairPerHour']

    @staticmethod
    def getWorkPlaceNames():
        """ Returns list of work place types names
        """
        workPlaces = PlaceInfo.getPlaceNames()
        workPlaces.remove("home")
        return workPlaces

    @staticmethod
    def getRankedPlaceNames():
        ranked = [k for k, v in sorted(PlaceInfo.placeTypes.items(), key=lambda item: item[1]['rank'])]
        placeNames = []
        for r in ranked:
            if r == 'store':
                for n in [t for t, c in sorted(list(PlaceInfo.storeTypes.items()), key=lambda e: e[1], reverse=True)]:
                    placeNames.append(n)
            else:
                placeNames.append(r)
        return placeNames

    @staticmethod
    def assignVisitFreq(placeName):
        low = PlaceInfo.placeTypes['store']['visit']['lowFreqDay']
        high = PlaceInfo.placeTypes['store']['visit']['highFreqDay']
        visitFreq = random.randint(high, low)
        if placeName.startswith('store'):
            storeType = 'store'
            if placeName.startswith('store_'):
                storeType = placeName[6:]
            visitFreq = visitFreq * sum(PlaceInfo.storeTypes.values()) / PlaceInfo.storeTypes[storeType]
        return visitFreq

    @staticmethod
    def assignVisitFreqs():
        return {placeName: PlaceInfo.assignVisitFreq(placeName) for placeName in PlaceInfo.getPlaceNames()}

    @staticmethod
    def assignWorkCapacity(placeName):
        if placeName.startswith('store_'):
            placeName = 'store'
        low = PlaceInfo.placeTypes[placeName]['work']['minCapacity']
        high = PlaceInfo.placeTypes[placeName]['work']['maxCapacity']
        return random.randint(low, high)

    @staticmethod
    def assignVisitCapacity(placeName):
        if placeName.startswith('store_'):
            placeName = 'store'
        low = PlaceInfo.placeTypes[placeName]['visit']['minCapacity']
        high = PlaceInfo.placeTypes[placeName]['visit']['maxCapacity']
        return random.randint(low, high)

    @staticmethod
    def assignHomeTypes(numPeople):
        percentagePeople = dict()
        weightTotal = 0.0
        for homeType, weight in PlaceInfo.homeTypes.items():
            newWeight = weight * (homeType[0] + homeType[1])
            percentagePeople[homeType] = newWeight
            weightTotal += newWeight
        for homeType, weight in percentagePeople.items():
            percentagePeople[homeType] = weight / weightTotal
        homeTypes = dict()
        totalPeople = 0
        sortedHomeTypes = sorted(PlaceInfo.homeTypes.keys(), key=lambda h: h[0] + h[1], reverse=True)
        for homeType in sortedHomeTypes:
            numPeopleInHome = homeType[0] + homeType[1]
            numHomes = int((numPeople * percentagePeople[homeType]) / numPeopleInHome)
            while totalPeople + numHomes * numPeopleInHome > numPeople:
                numHomes -= 1
            homeTypes[homeType] = numHomes
            totalPeople += numHomes * numPeopleInHome
        while totalPeople + sortedHomeTypes[len(sortedHomeTypes) - 1][0] + sortedHomeTypes[len(sortedHomeTypes) - 1][1]\
                <= numPeople:
            homeTypes[sortedHomeTypes[len(sortedHomeTypes) - 1]] += 1
            totalPeople += sortedHomeTypes[len(sortedHomeTypes) - 1][0] + sortedHomeTypes[len(sortedHomeTypes) - 1][1]
        return homeTypes

    @staticmethod
    def _assignTimes(placeName, date, timeType):
        if placeName.startswith('store_'):
            placeName = 'store'
        timeLow = datetime.datetime.strptime(PlaceInfo.placeTypes[placeName][timeType]['minArrive'], "%H:%M:%S").time()
        timeHigh = datetime.datetime.strptime(PlaceInfo.placeTypes[placeName][timeType]['maxArrive'], "%H:%M:%S").time()
        dateLow = datetime.datetime.combine(date, timeLow)
        dateHigh = datetime.datetime.combine(date, timeHigh)
        begin = dateLow + datetime.timedelta(seconds=random.randint(0, int((dateHigh - dateLow).total_seconds())))
        lengthLow = PlaceInfo.placeTypes[placeName][timeType]['minLengthMin']
        lengthHigh = PlaceInfo.placeTypes[placeName][timeType]['maxLengthMin']
        end = begin + datetime.timedelta(minutes=random.randint(lengthLow, lengthHigh))
        return begin, end

    @staticmethod
    def assignWorkTimes(placeName, date):
        return PlaceInfo._assignTimes(placeName, date, 'work')

    @staticmethod
    def assignVisitTimes(placeName, date):
        return PlaceInfo._assignTimes(placeName, date, 'visit')

    @staticmethod
    def getAverageVisitMin(placeName):
        if placeName.startswith('store_'):
            placeName = 'store'
        low = PlaceInfo.placeTypes[placeName]['visit']['minLengthMin']
        high = PlaceInfo.placeTypes[placeName]['visit']['maxLengthMin']
        return int((high - low) / 2.0)

    @staticmethod
    def getDailyVisitMin(placeName):
        if placeName.startswith('store_'):
            placeName = 'store'
        start = datetime.datetime.strptime(PlaceInfo.placeTypes[placeName]['visit']['minArrive'], "%H:%M:%S")
        end = datetime.datetime.strptime(PlaceInfo.placeTypes[placeName]['visit']['maxArrive'], "%H:%M:%S")
        return int((end - start).total_seconds() / 60.0 * PlaceInfo.placeTypes[placeName]['visit']['avgOccupancy'])

    @staticmethod
    def defaultNormalPolicyData():
        policy = dict()
        for placeName, placeDict in PlaceInfo.placeTypes.items():
            if placeName == 'store':
                for pn in PlaceInfo.sortedStoreTypes():
                    policy[pn] = {
                        'work': {
                            'open': placeDict['work']['open'],
                            'happening': placeDict['work']['happening'],
                        },
                        'visit': {
                            'open': placeDict['visit']['open'],
                            'happening': placeDict['visit']['happening'],
                        },
                    }
            else:
                policy[placeName] = {
                    'work': {
                        'open': placeDict['work']['open'],
                        'happening': placeDict['work']['happening'],
                    },
                    'visit': {
                        'open': placeDict['visit']['open'],
                        'happening': placeDict['visit']['happening'],
                    },
                }
        return policy

    @staticmethod
    def assignNumApt():
        r = random.choices(list(PlaceInfo.houseTypes.keys()), weights=PlaceInfo.houseTypes.values(), k=1)[0]
        if r == 1 or r == 2:
            return r
        elif r == 3:
            return random.randint(3, 6)
            #  return random.choices(range(3, 7), weights=[9, 5.6, 3, 2], k=1)[0]
        elif r == 7:
            return random.randint(7, 12)
            #  return random.choices(range(7, 13), weights=[2, 1, 1, 0.8, 0.6, 0.6], k=1)[0]
        else:
            return random.randint(13, 80)
            #  return random.choices(range(13, 21), weights=[0.4, 0.4, 0.3, 0.3, 0.2, 0.2, 0.1, 0.1], k=1)[0]

    @staticmethod
    def sortedStoreTypes():
        return [f"store_{t}" if t != 'store' else 'store' for t, c in sorted(list(PlaceInfo.storeTypes.items()),
                                                                             key=lambda e: e[1], reverse=True)]


class Place:
    """ Represents a single place. A place has a name and two capacities, a capacity for workers and one for visitors.
    The name of a place is formed as "placeName-number", e.g., "office-42" for the 43rd office created. Capacities are
    assigned utilizing a PlaceInfo object.
    """
    @staticmethod
    def _dailyAmounts(people):
        dailyWorkSchool = 0
        dailyWorkNonSchool = 0
        dailyVisits = dict()
        for placeName in PlaceInfo.getWorkPlaceNames():
            if placeName not in dailyVisits:
                dailyVisits[placeName] = 0
        for person in people:
            if person.works:
                if person.hasSchoolAge():
                    dailyWorkSchool = dailyWorkSchool + 1
                else:
                    dailyWorkNonSchool = dailyWorkNonSchool + 1
            if person.visits:
                for placeName in PlaceInfo.getWorkPlaceNames():
                    if person.visitFreqs[placeName] > 0:
                        dailyVisits[placeName] = dailyVisits[placeName] + (1.0 / person.visitFreqs[placeName])
        return dailyWorkSchool, dailyWorkNonSchool, dailyVisits

    @staticmethod
    def generateWorkPlaces(people, placeAddressTracker):
        """
        Returns dictionary with one list of places per place type. Takes a iterable of Person objects.
        Each Person object must have methods "int works(atPlaceName=None)" and "int visitFreqs(placeName)".
        This method assumes that place types 'school' and 'office' exist.
        :param people: Iterable of Person objects.
        :param placeAddressTracker: PlaceAddressTracker instance
        :return: Dictionary with one list of places per place type.
        """
        WarningCounter.reset()
        dailyWorkSchool, dailyWorkNonSchool, dailyVisits = Place._dailyAmounts(people)
        dailyWorkSchoolRemaining = dailyWorkSchool
        dailyWorkOfficeRemaining = dailyWorkNonSchool
        places = dict()
        for placeName in PlaceInfo.getWorkPlaceNames():
            places[placeName] = []
            dailyVisitMin = PlaceInfo.getDailyVisitMin(placeName)
            averageVisitMin = PlaceInfo.getAverageVisitMin(placeName)
            dailyVisitCapacity = 0
            while dailyVisitCapacity * dailyVisitMin < dailyVisits[placeName] * averageVisitMin:
                lat, lon = placeAddressTracker.getAddress(placeName, force=True)
                place = Place(len(places[placeName]), placeName, lat, lon)
                places[placeName].append(place)
                dailyVisitCapacity = dailyVisitCapacity + place.visitCapacity
                if placeName == 'school':
                    dailyWorkSchoolRemaining = dailyWorkSchoolRemaining - place.workCapacity
                else:
                    dailyWorkOfficeRemaining = dailyWorkOfficeRemaining - place.workCapacity
        while dailyWorkSchoolRemaining > 0:
            lat, lon = placeAddressTracker.getAddress('school', force=True)
            place = Place(len(places["school"]), "school", lat, lon)
            places["school"].append(place)
            dailyWorkSchoolRemaining = dailyWorkSchoolRemaining - place.workCapacity
        while dailyWorkOfficeRemaining > 0:
            lat, lon = placeAddressTracker.getAddress('office', force=True)
            place = Place(len(places["office"]), "office", lat, lon)
            places["office"].append(place)
            dailyWorkOfficeRemaining = dailyWorkOfficeRemaining - place.workCapacity
        WarningCounter.print()
        return places

    @staticmethod
    def generateHomes(numPeople, placeAddressTracker):
        """
        Returns dictionary with one list of homes per type of homes. Takes a number of people.
        Home types are tuples (a, c) where a is the number of adults and c the number of children in the home.
        :param numPeople: Number of people.
        :param placeAddressTracker: PlaceAddressTracker instance
        :return: Dictionary with one list of homes per type of homes.
        """
        WarningCounter.reset()
        homeTypes = PlaceInfo.assignHomeTypes(numPeople)
        homes = dict()
        count = 0
        for homeType, numHomes in homeTypes.items():
            homes[homeType] = []
            numMembers = homeType[0] + homeType[1]
            for i in range(numHomes):
                lat, lon = placeAddressTracker.getAddress('home', force=True)
                homes[homeType].append(Place(count, 'home', lat, lon, workCapacity=numMembers))
                count += 1
        WarningCounter.print()
        return homes

    @staticmethod
    def populateHomesDb(homes, cur, conn):
        """
            Creates a 'homes' table in the database and populates it with homes data
        """
        sql = '''DROP TABLE IF EXISTS homes;'''
        cur.execute(sql)
        sql = '''CREATE TABLE IF NOT EXISTS homes(
                name text,
                adults int,
                children int,
                people int,
                lat real,
                lon real,
                work_capacity int,
                visit_capacity int
            );'''
        cur.execute(sql)
        for homeType in homes:
            (adults, children) = homeType
            people = adults + children
            for home in homes[homeType]:
                sql = f'''
                    INSERT INTO homes VALUES(
                        '{home.name}',
                        {adults},
                        {children},
                        {people},
                        {home.lat},
                        {home.lon},
                        {home.workCapacity},
                        {home.visitCapacity}
                    );
                '''
                cur.execute(sql)
        conn.commit()
        return

    @staticmethod
    def populateWorkPlacesDb(workPlaces, cur, conn):
        """
            Creates a 'workPlaces' table in the database and populates it with workPlaces data
        """
        sql = '''DROP TABLE IF EXISTS workPlaces;'''
        cur.execute(sql)
        sql = '''CREATE TABLE IF NOT EXISTS workPlaces(
                name text,
                type text,
                lat real,
                lon real,
                work_capacity int,
                visit_capacity int
            );'''
        cur.execute(sql)
        for placeType in workPlaces:
            for place in workPlaces[placeType]:
                sql = f'''
                    INSERT INTO workPlaces VALUES(
                        '{place.name}',
                        '{placeType}',
                        {place.lat},
                        {place.lon},
                        {place.workCapacity},
                        {place.visitCapacity}
                    );
                '''
                cur.execute(sql)
        conn.commit()
        return

    def __init__(self, number, placeName, lat, lon, workCapacity=None, visitCapacity=None):
        self.name = f"{placeName}-{number}"
        self.placeName = placeName
        self.lat = lat
        self.lon = lon
        if workCapacity is None:
            workCapacity = PlaceInfo.assignWorkCapacity(placeName)
        self.workCapacity = workCapacity
        if visitCapacity is None:
            visitCapacity = PlaceInfo.assignVisitCapacity(placeName)
        self.visitCapacity = visitCapacity


class PlaceCapacityTracker:
    """
    Helps keeping track of place capacities while assigning people to places as workers or visitors.
    """
    def __init__(self):
        self.places = dict()

    def _checkExists(self, place):
        if place not in self.places:
            self.places[place] = [place.workCapacity, place.visitCapacity * PlaceInfo.getDailyVisitMin(place.placeName)]

    def remainingWorkCapacity(self, place):
        self._checkExists(place)
        return self.places[place][0]

    def remainingVisitCapacity(self, place):
        self._checkExists(place)
        return self.places[place][1]

    def hasWorkCapacity(self, place):
        if self.remainingWorkCapacity(place) > 0:
            return True
        return False

    def hasVisitCapacity(self, place):
        if self.remainingVisitCapacity(place) > 0:
            return True
        return False

    def hasVisitCapacityFor(self, place, requiredCapacity):
        if self.remainingVisitCapacity(place) >= requiredCapacity * PlaceInfo.getAverageVisitMin(place.placeName):
            return True
        return False

    def useWorkCapacity(self, place):
        if not self.hasWorkCapacity(place):
            raise ValueError(f"Not enough work capacity in place {place.name}")
        self.places[place][0] -= 1

    def useVisitCapacity(self, place, requiredCapacity, force=False):
        if not force and not self.hasVisitCapacityFor(place, requiredCapacity):
            raise ValueError(f"Not enough visit capacity in place {place.name}")
        self.places[place][1] -= requiredCapacity * PlaceInfo.getAverageVisitMin(place.placeName)


class PlaceAddressTracker:
    """
    Helps assigning addresses to different types of places
    """
    order = {
        'home': ['home', 'other'],
        'school': ['school', 'store', 'other'],
        'office': ['office', 'store', 'other'],
        'sport': ['sport', 'school', 'other'],
        'super': ['store', 'other'],
        'store': ['store', 'other'],
        'restaurant': ['restaurant', 'other'],
    }

    gps = {
        'minLat': 49.423043,
        'maxLat': 49.454434,
        'minLon': 7.726833,
        'maxLon': 7.808753,
    }

    @staticmethod
    def fakeGpsForPlace():
        latRange = PlaceAddressTracker.gps['maxLat'] - PlaceAddressTracker.gps['minLat']
        lonRange = PlaceAddressTracker.gps['maxLon'] - PlaceAddressTracker.gps['minLon']
        lat = (random.random() * latRange) + PlaceAddressTracker.gps['minLat']
        lon = (random.random() * lonRange) + PlaceAddressTracker.gps['minLon']
        return lat, lon

    @staticmethod
    def loadAddresses(pathToAddresses):
        with open(pathToAddresses) as f:
            return PlaceAddressTracker(json.load(f))

    def __init__(self, addresses):
        self._statistics = {pn: [len(lst), len(lst)] for pn, lst in addresses.items()}
        self._order = PlaceAddressTracker.order.copy()
        if 'home' in addresses:
            newHomes = []
            for home in addresses['home']:
                for _ in range(PlaceInfo.assignNumApt()):
                    newHomes.append(home)
            addresses['home'] = newHomes
            self._statistics['home'][1] = len(newHomes)
        if 'store' in addresses:
            for pn, lst in self._splitStores(addresses['store']).items():
                addresses[pn] = lst
                self._statistics[pn] = [len(lst), len(lst)]
        for pn, lst in addresses.items():
            random.shuffle(lst)
        self._addresses = addresses

    def _splitStores(self, stores):
        newStores = dict()
        for store in stores:
            labels = list()
            if 'shop' in store:
                if store['shop'] in PlaceInfo.storeTypes:
                    labels.append(store['shop'])
            if 'amenity' in store:
                if store['amenity'] in PlaceInfo.storeTypes:
                    labels.append(store['amenity'])
            if not labels:
                labels.append('store')
            for label in labels:
                newLabel = 'store_' + label
                if label == 'store':
                    newLabel = 'store'
                if newLabel not in newStores:
                    newStores[newLabel] = list()
                    if newLabel not in self._order:
                        self._order[newLabel] = [newLabel, 'store', 'other']
                newStores[newLabel].append(store)
        return newStores

    def hasAddress(self, placeName):
        if placeName not in self._addresses:
            return False
        if self._addresses[placeName]:
            return True
        return False

    def getAddress(self, placeName, force=False):
        if self.hasAddress(placeName):
            place = self._addresses[placeName].pop(0)
            return float(place['lat']), float(place['lon'])
        if not force:
            raise ValueError("No address available.")
        if placeName in self._order:
            for pn in self._order[placeName]:
                if self.hasAddress(pn):
                    place = self._addresses[pn].pop(0)
                    return float(place['lat']), float(place['lon'])
        WarningCounter.count(f"Failed to get address for place type {placeName}. Returned fake address.")
        return PlaceAddressTracker.fakeGpsForPlace()

    def printStats(self):
        print(f"| ADDRESS Statistics")
        for pn, lst in self._addresses.items():
            print(f"|    {pn}: {self._statistics[pn][1] - len(lst)} "
                  f"({(self._statistics[pn][1] - len(lst)) / self._statistics[pn][1] * 100:.1f}%) used of "
                  f"{self._statistics[pn][1]} (originally, {self._statistics[pn][0]} distinct).")


if __name__ == '__main__':
    print(PlaceInfo.getPlaceNames())
    print("assignVisitFreq():")
    print(f"    office: {PlaceInfo.assignVisitFreq('office')}")
    print(f"    school: {PlaceInfo.assignVisitFreq('school')}")
