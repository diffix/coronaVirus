import datetime
import enum


class Gender(enum.Enum):
    """
    gender enumerator.
    terms:
        - FEMALE : 0
        - MALE : 1
        - OTHER : 2

    #usage
        - list of all genders: `list(Gender)`
        - cast to string:
            - e.g: `str(common.Gender.FEMALE)`
        - cast to enum
            - e.g: `common.Gender['MALE']`
    """
    FEMALE = 0
    MALE = 1
    OTHER = 2

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return self.__str__()


class WarningCounter:
    instances = dict()

    @staticmethod
    def count(warning):
        if warning not in WarningCounter.instances:
            WarningCounter.instances[warning] = 0
        WarningCounter.instances[warning] += 1

    @staticmethod
    def reset():
        WarningCounter.instances.clear()

    @staticmethod
    def print():
        for warning, count in WarningCounter.instances.items():
            print(f"WARNING occurred {count} times: {warning}")


class ElapsedTimer:
    def __init__(self):
        self._startTime = None
        self._lastTime = None

    def start(self):
        self._startTime = datetime.datetime.now()
        self._lastTime = self._startTime
        print(f"|==============================\n| START\n|------------------------------")

    def printElapsed(self):
        nowTime = datetime.datetime.now()
        elapsedTime = nowTime - self._startTime
        sinceLastTime = nowTime - self._lastTime
        self._lastTime = nowTime
        print(f"|------------------------------\n| Elapsed time: {elapsedTime} ({sinceLastTime} since last)\n"
              f"|------------------------------")

    def finish(self):
        self._startTime = None
        self._lastTime = self._startTime
        print(f"| FINISH\n|==============================")
