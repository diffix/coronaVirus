import random
from place import PlaceInfo


class Policy:
    """
    The 'open' parameter is the ratio of places that stay open for
        the type of stay ('work' or 'visit'). These are fixed in the
        policy, so the same places are open while using the same policy instance.
    The 'happening' parameter for 'work' is the ratio of workers that
        are still working. These are fixed in the person policy.
    The 'happening' parameter for 'visit' is the ratio of visits
        that still happen. Here it is decided randomly for each visit
        anyone wants to make.
    The placeTypes variable additionally contains the data for the
        default "normal" policy. The additional defaultRestrictiveData
        variable contains the data for the default "restrictive" policy.
        You may create your own PlacePolicy by providing a policy object
        that follows the structure of defaultRestrictiveData. You can then
        create your own PersonPolicy with that PlacePolicy. PersonPolicy
        takes all its parameters from PlacePolicy.
    """
    defaultRestrictiveBaseData = {
        'home': {
            'work': {
                'open': 1.0,
                'happening': 1.0,
            },
            'visit': {
                'open': 0.5,
                'happening': 0.2,
            },
        },
        'school': {
            'work': {
                'open': 1.0,
                'happening': 0.01,
            },
            'visit': {
                'open': 0.0,
                'happening': 0.0,
            },
        },
        'office': {
            'work': {
                'open': 0.1,
                'happening': 0.2,
            },
            'visit': {
                'open': 0.0,
                'happening': 0.0,
            },
        },
        'sport': {
            'work': {
                'open': 0.0,
                'happening': 0.0,
            },
            'visit': {
                'open': 0.0,
                'happening': 0.0,
            },
        },
        'super': {
            'work': {
                'open': 1.0,
                'happening': 1.0,
            },
            'visit': {
                'open': 1.0,
                'happening': 1.0,
            },
        },
        'store': {
            'work': {
                'open': 0.2,
                'happening': 1.0,
            },
            'visit': {
                'open': 0.2,
                'happening': 0.5,
            },
        },
        'restaurant': {
            'work': {
                'open': 0.5,
                'happening': 1.0,
            },
            'visit': {
                'open': 0.0,
                'happening': 0.0,
            },
        },
    }

    @staticmethod
    def defaultRestrictiveData():
        data = Policy.defaultRestrictiveBaseData.copy()
        for pn in PlaceInfo.sortedStoreTypes():
            data[pn] = data['store']
        return data

    @staticmethod
    def defaultNormal(people, homes, workPlaces):
        return Policy(people, homes, workPlaces, PlaceInfo.defaultNormalPolicyData())

    @staticmethod
    def defaultRestrictive(people, homes, workPlaces):
        return Policy(people, homes, workPlaces, Policy.defaultRestrictiveData())

    def __init__(self, people, homes, workPlaces, policy):
        self._policy = policy
        self._places = dict()
        self._people = dict()
        for homesLst in homes.values():
            self._addPlaces(homesLst)
        for placeLst in workPlaces.values():
            self._addPlaces(placeLst)
        self._addPeople(people)

    def getPlaces(self, placeName):
        return list(self._places[placeName].keys())

    def getPeople(self):
        return list(self._people.keys())

    def _addPlaces(self, places):
        for place in places:
            if place.placeName not in self._places:
                self._places[place.placeName] = dict()
            if place in self._places[place.placeName]:
                continue
            self._initPlace(place)

    def _initPlace(self, place):
        openWork = random.random() < self._policy[place.placeName]['work']['open']
        openVisits = random.random() < self._policy[place.placeName]['visit']['open'] if openWork else False
        self._places[place.placeName][place] = [openWork, openVisits, []]

    def _addPeople(self, people):
        for person in people:
            if person in self._people:
                continue
            self._initPerson(person)

    def _initPerson(self, person):
        if person.works:
            self._people[person] = self._assignWorking(person.work)
            self._places[person.work.placeName][person.work][2].append(person)
        else:
            self._people[person] = False

    def _assignWorking(self, place):
        if not self._places[place.placeName][place][0]:
            return False
        return random.random() < self._policy[place.placeName]['work']['happening']

    @staticmethod
    def _randomSplitPlaces(placeDct):
        woVo, woVc, wcVc = [], [], []  # w=work V=visits o=open c=closed
        for place, data in placeDct.items():
            (wcVc if not data[0] else woVo if data[1] else woVc).append(place)
        random.shuffle(woVo)
        random.shuffle(woVc)
        random.shuffle(wcVc)
        return woVo, woVc, wcVc

    def _calculateRemainingChoices(self, placeName, placeDct):
        woVo, woVc, wcVc = Policy._randomSplitPlaces(placeDct)  # w=work V=visits o=open c=closed
        newChoices = [(random.random() < self._policy[placeName]['work']['open'],
                       random.random() < self._policy[placeName]['visit']['open']) for _ in range(len(placeDct))]
        woVoR, woVcR, wcVcR = 0, 0, 0  # w=work V=visits o=open c=closed R=remaining
        for choice in newChoices:
            if not choice[0]:  # if work is not open
                if wcVc:
                    del wcVc[0]
                else:
                    wcVcR += 1
            elif not choice[1]:  # if work is open and visits are closed
                if woVc:
                    del woVc[0]
                else:
                    woVcR += 1
            else:  # if work is open and visits are open
                if woVo:
                    del woVo[0]
                else:
                    woVoR += 1
        return woVo, woVc, wcVc, woVoR, woVcR, wcVcR

    def _modify(self, placeName=None):
        for pn, pd in self._places.items():
            if placeName is not None and pn != placeName:
                continue
            woVo, woVc, wcVc, woVoR, woVcR, wcVcR = self._calculateRemainingChoices(pn, pd)
            # w=work V=visits o=open c=closed R=remaining
            while woVcR > 0 and woVo:
                woVcR -= 1
                pd[woVo.pop(0)][1] = False
            while woVoR > 0 and woVc:
                woVoR -= 1
                pd[woVc.pop(0)][1] = True
            while woVcR > 0 and wcVc:
                woVcR -= 1
                place = wcVc.pop(0)
                pd[place][0] = True
                for person in pd[place][2]:
                    self._people[person] = self._assignWorking(person.work)
            while woVoR > 0 and wcVc:
                woVoR -= 1
                place = wcVc.pop(0)
                pd[place][0] = True
                pd[place][1] = True
                for person in pd[place][2]:
                    self._people[person] = self._assignWorking(person.work)
            while wcVcR > 0:
                wcVcR -= 1
                place = woVc.pop(0) if woVc else woVo.pop(0)
                pd[place][0] = False
                pd[place][1] = False
                for person in pd[place][2]:
                    self._people[person] = False

    def reset(self):
        for placeDct in self._places.values():
            for place in placeDct:
                self._initPlace(place)
        for person in self._people:
            self._initPerson(person)

    def modifyPlaces(self, placeName, keepOpen, visitorsAllowed, keepWorking, keepVisiting):
        self._policy[placeName]['work']['open'] = keepOpen
        self._policy[placeName]['visit']['open'] = visitorsAllowed
        self._policy[placeName]['work']['happening'] = keepWorking
        self._policy[placeName]['visit']['happening'] = keepVisiting
        self._modify(placeName=placeName)

    def closePlaces(self, placeName, keepOpen=0.0, visitorsAllowed=1.0, keepWorking=1.0, keepVisiting=1.0):
        self.modifyPlaces(placeName, keepOpen, visitorsAllowed, keepWorking, keepVisiting)

    def openPlaces(self, placeName, keepClosed=0.0, visitorsAllowed=1.0, stayHome=0.0, doNotVisit=0.0):
        self.modifyPlaces(placeName, 1.0 - keepClosed, visitorsAllowed, 1.0 - stayHome, 1.0 - doNotVisit)

    def decideVisit(self, place):
        if not self._places[place.placeName][place][1]:
            return False
        return random.random() < self._policy[place.placeName]['visit']['happening']

    def isWorking(self, person):
        return self._people[person]
