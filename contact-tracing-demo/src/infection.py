import datetime
import random
from dataAccess import Symptom


class InfectionInfo:
    transmissionProbability = 0.275
    symptomsAfterMinutesMin = 120
    symptomsAfterMinutesMax = 180

    @staticmethod
    def assignTransmission():
        return random.random() < InfectionInfo.transmissionProbability

    @staticmethod
    def assignSymptomsAfterMinutes():
        return random.randint(InfectionInfo.symptomsAfterMinutesMin, InfectionInfo.symptomsAfterMinutesMax)


class Infection:
    @staticmethod
    def _determineStartPid(encounters, people, startRole):
        if startRole is not None:
            if people is None:
                raise ValueError("people cannot be None if startRole is set")
            pid = None
            pids = list(people.keys())
            while pid is None or people[pid].role != startRole:
                pid = random.choice(pids)
            return pid
        return random.choice(encounters).pid1

    @staticmethod
    def infect(encounters, people=None, startPid=None, startRole=None):
        if startPid is None:
            startPid = Infection._determineStartPid(encounters, people, startRole)
        infected = {startPid}
        encounters.sort(key=lambda e: e.time)
        symptoms = list()
        firstTime = None
        lastTime = None
        for encounter in encounters:
            if firstTime is None:
                firstTime = encounter.time
            lastTime = encounter.time
            p1i = encounter.pid1 in infected
            p2i = encounter.pid2 in infected
            if (p1i and p2i) or (not p1i and not p2i):
                continue
            if InfectionInfo.assignTransmission():
                if not p1i:
                    infected.add(encounter.pid1)
                    symptoms.append(Symptom(pid=encounter.pid1, time=encounter.time + datetime.timedelta(
                        minutes=InfectionInfo.assignSymptomsAfterMinutes())))
                if not p2i:
                    infected.add(encounter.pid2)
                    symptoms.append(Symptom(pid=encounter.pid2, time=encounter.time + datetime.timedelta(
                        minutes=InfectionInfo.assignSymptomsAfterMinutes())))
        durationInDays = (lastTime - firstTime).total_seconds() / (24.0 * 3600.0)
        print(f"| Infection with startPid={startPid}")
        print(f"|    Time frame of encounters in days: {durationInDays:.2f}")
        print(f"|    Total number of infections during that time: {len(symptoms)}")
        print(f"|    Average infections per day: {len(symptoms) / durationInDays:.2f}")
        return symptoms
