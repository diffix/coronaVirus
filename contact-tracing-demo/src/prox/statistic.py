from person import PersonInfo


class Statistic:
    @staticmethod
    def _sumMultiplied(lst):
        return sum(map(lambda item: item[0] * item[1], lst))

    @staticmethod
    def _sumCounts(lst):
        return sum(map(lambda item: item[1], lst))

    @staticmethod
    def _placesPerType(places):
        types = dict()
        for place in places:
            if place.placeName not in types:
                types[place.placeName] = 0
            types[place.placeName] += 1
        return sorted([(t, v) for t, v in types.items()], key=lambda item: item[0])

    @staticmethod
    def _placesPerTypePer(places, accessFunction):
        types = dict()
        for place in places:
            if place.placeName not in types:
                types[place.placeName] = dict()
            key = accessFunction(place)
            if key not in types[place.placeName]:
                types[place.placeName][key] = 0
            types[place.placeName][key] += 1
        return {
            t: sorted([(k, v) for k, v in d.items()], key=lambda item: item[0]) for t, d in types.items()
        }

    @staticmethod
    def _workersPerType(people):
        places = dict()
        for person in people:
            if not person.work:
                continue
            if person.work not in places:
                places[person.work] = 0
            places[person.work] += 1
        countsPerType = dict()
        for place, count in places.items():
            if place.placeName not in countsPerType:
                countsPerType[place.placeName] = dict()
            if count not in countsPerType[place.placeName]:
                countsPerType[place.placeName][count] = 0
            countsPerType[place.placeName][count] += 1
        return {
             t: sorted([(c, v) for c, v in d.items()], key=lambda item: item[0]) for t, d in countsPerType.items()
        }

    @staticmethod
    def _staysPerType(visits):
        staysPerType = dict()
        for place in visits:
            numStays = len(visits[place])
            if place.placeName not in staysPerType:
                staysPerType[place.placeName] = dict()
            if numStays not in staysPerType[place.placeName]:
                staysPerType[place.placeName][numStays] = 0
            staysPerType[place.placeName][numStays] += 1
        return {
            t: sorted([(c, v) for c, v in d.items()], key=lambda item: item[0]) for t, d in staysPerType.items()
        }

    @staticmethod
    def _printPlacesPer(places, accessFunction, variable, variableName):
        valuesPerType = Statistic._placesPerTypePer(places, accessFunction)
        print(f"| How many places of type t have {variable} {variableName}? "
              f"--> t: sum(#), sum({variable} * #) = [({variable}, #)]")
        for t in sorted(list(valuesPerType.keys())):
            print(f"| {t}: {Statistic._sumCounts(valuesPerType[t])}, {Statistic._sumMultiplied(valuesPerType[t])} "
                  f"= {valuesPerType[t]}")
        print(f"|")

    @staticmethod
    def printPlaceStatistics(visits):
        places = list(visits.keys())
        print(f"| How many places exist? --> #\n| {len(places)}\n|")
        placesPerType = Statistic._placesPerType(places)
        print(f"| How many places of type t exist? --> sum(#) = [(t, #)]\n"
              f"| {Statistic._sumCounts(placesPerType)} = {placesPerType}\n|")
        Statistic._printPlacesPer(places, lambda place: place.workCapacity, 'w', "work capacity")
        workersPerType = Statistic._workersPerType(Statistic._peopleAndStayCounts(visits)[0])
        print(f"| How many places of type t have p people working? --> t: sum(#), sum(p * #) = [(p, #)]")
        for t in sorted(list(workersPerType.keys())):
            print(f"| {t}: {Statistic._sumCounts(workersPerType[t])}, {Statistic._sumMultiplied(workersPerType[t])} "
                  f"= {workersPerType[t]}")
        print(f"|")
        Statistic._printPlacesPer(places, lambda place: place.visitCapacity, 'v', "visit capacity")
        staysPerType = Statistic._staysPerType(visits)
        print(f"| How many places of type t have s stays? --> t: sum(#), sum(s * #) = [(s, #)]")
        for t in sorted(list(staysPerType.keys())):
            print(f"| {t}: {Statistic._sumCounts(staysPerType[t])}, {Statistic._sumMultiplied(staysPerType[t])} "
                  f"= {staysPerType[t]}")
        print(f"|")

    @staticmethod
    def _peopleAndStayCounts(visits):
        numStays = dict()
        for visitLst in visits.values():
            for visit in visitLst:
                if visit[0] not in numStays:
                    numStays[visit[0]] = 0
                numStays[visit[0]] += 1
        numCounts = dict()
        for count in numStays.values():
            if count not in numCounts:
                numCounts[count] = 0
            numCounts[count] += 1
        return list(numStays.keys()), sorted([(c, v) for c, v in numCounts.items()], key=lambda item: item[0])

    @staticmethod
    def _peoplePer(people, accessFunction):
        counts = dict()
        for person in people:
            key = accessFunction(person)
            if key not in counts:
                counts[key] = 0
            counts[key] += 1
        return sorted([(k, v) for k, v in counts.items()], key=lambda item: item[0])

    @staticmethod
    def _peoplePerAgeRange(people):
        counts = {
            'childAge': 0,
            'adultAge': 0,
            'schoolAge': 0,
            'workAge': 0,
            'visitAge': 0,
        }
        for person in people:
            if PersonInfo.hasChildAge(person.age):
                counts['childAge'] += 1
            if PersonInfo.hasAdultAge(person.age):
                counts['adultAge'] += 1
            if PersonInfo.hasSchoolAge(person.age):
                counts['schoolAge'] += 1
            if PersonInfo.hasWorkAge(person.age):
                counts['workAge'] += 1
            if PersonInfo.hasVisitAge(person.age):
                counts['visitAge'] += 1
        return sorted([(v, c) for v, c in counts.items()], key=lambda item: item[0])

    @staticmethod
    def _visitFrequenciesPerPlaceType(people):
        frequencies = dict()
        for person in people:
            for placeType, frequency in person.visitFreqs.items():
                if placeType not in frequencies:
                    frequencies[placeType] = dict()
                if frequency not in frequencies[placeType]:
                    frequencies[placeType][frequency] = 0
                frequencies[placeType][frequency] += 1
        return {
            t: sorted([(c, v) for c, v in d.items()], key=lambda item: item[0]) for t, d in frequencies.items()
        }

    @staticmethod
    def printPeopleStatistics(visits):
        people, stayCounts = Statistic._peopleAndStayCounts(visits)
        print(f"| How many people exist? --> #\n| {len(people)}\n|")
        peoplePerAge = Statistic._peoplePer(people, lambda p: p.age)
        print(f"| How many people have age a? --> sum(#) = [(a, #)]\n"
              f"| {Statistic._sumCounts(peoplePerAge)} = {peoplePerAge}\n|")
        peoplePerAgeRange = Statistic._peoplePerAgeRange(people)
        print(f"| How many people are in age range r? --> sum(#) = [(r, #)]\n"
              f"| {Statistic._sumCounts(peoplePerAgeRange)} = {peoplePerAgeRange}\n|")
        peoplePerGender = Statistic._peoplePer(people, lambda p: str(p.gender))
        print(f"| How many people have gender g? --> sum(#) = [(g, #)]\n"
              f"| {Statistic._sumCounts(peoplePerGender)} = {peoplePerGender}\n|")
        print(f"| How many people work? --> #\n| {len([p for p in people if p.works])}\n|")
        print(f"| How many people visit? --> #\n| {len([p for p in people if p.visits])}\n|")
        print(f"| How many people are at risk? --> #\n| {len([p for p in people if p.atRisk])}\n|")
        visitFrequenciesPerType = Statistic._visitFrequenciesPerPlaceType(people)
        print(f"| How many people visit places of type t with frequency f? --> t: sum(#) = [(f, #)]")
        for t in sorted(list(visitFrequenciesPerType.keys())):
            print(f"| {t}: {Statistic._sumCounts(visitFrequenciesPerType[t])} = {visitFrequenciesPerType[t]}")
        print(f"|")
        print(f"| How many people have s stays? --> sum(#), sum(s * #) = [(s, #)]\n"
              f"| {Statistic._sumCounts(stayCounts)}, {Statistic._sumMultiplied(stayCounts)} = {stayCounts}\n|")

    @staticmethod
    def printStatistics(visits):
        print(f"|-----\n| STATISTICS\n|")
        Statistic.printPlaceStatistics(visits)
        Statistic.printPeopleStatistics(visits)
        print(f"|-----")
