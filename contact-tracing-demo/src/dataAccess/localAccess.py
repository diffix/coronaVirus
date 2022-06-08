import csv
import datetime
import sqlite3


class LocalAccess:
    @staticmethod
    def personFrom(row):
        id_ = row[0]
        age = row[1]
        gender = row[2]
        atRisk = row[3]
        role = row[4]
        home = row[5]
        work = row[6]
        visitFreqs = {
            'home': row[7],
            'school': row[8],
            'office': row[9],
            'sport': row[10],
            'super': row[11],
            'store': row[12],
            'restaurant': row[13],
        }
        favPlaces = {
            'home': (row[14], row[15]),
            'school': (row[16], row[17]),
            'office': (row[18], row[19]),
            'sport': (row[20], row[21]),
            'super': (row[22], row[23]),
            'store': (row[24], row[25]),
            'restaurant': (row[26], row[27]),
        }
        return Person(id_, age, gender, atRisk, role, home, work, visitFreqs, favPlaces)

    @staticmethod
    def encounterFrom(row):
        pid1 = row[0]
        pid2 = row[1]
        placeName = row[2]
        placeType = row[3]
        lat = row[4]
        lon = row[5]
        time = datetime.datetime.strptime(row[6], "%Y-%m-%d %H:%M:%S")
        return Encounter(pid1, pid2, placeName, placeType, lat, lon, time)

    @staticmethod
    def writeToCsv(pathToCsvFile, lst):
        with open(pathToCsvFile, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(map(lambda o: o.listOfStrings(), lst))

    def __init__(self, pathToDbFile):
        self._conn = sqlite3.connect(pathToDbFile)

    def __del__(self):
        self._conn.close()

    def _execute(self, sql):
        cursor = self._conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    def saveToTable(self, objects):
        if not objects:
            return
        first = objects[0]
        cursor = self._conn.cursor()
        cursor.execute(first.sqlDropTable())
        cursor.execute(first.sqlCreateTable())
        for o in objects:
            cursor.execute(o.sqlInsertInto())
        self._conn.commit()

    def loadPeople(self):
        return {row[0]: LocalAccess.personFrom(row) for row in self._execute("SELECT * FROM people;")}

    def loadEncounters(self):
        return [LocalAccess.encounterFrom(row) for row in self._execute("SELECT * FROM encounters;")]


class Person:
    def __init__(self, id_=None, age=None, gender=None, atRisk=None, role=None, home=None, work=None, visitFreqs=None,
                 favPlaces=None):
        self.id_ = id_
        self.age = age
        self.gender = gender
        self.atRisk = atRisk
        self.role = role
        self.home = home
        self.work = work
        self.visitFreqs = visitFreqs
        self.favPlaces = favPlaces

    def __str__(self):
        return f"Person: {self.listOfStrings()}"

    __repr__ = __str__

    def listOfStrings(self):
        return [f"{v}" for v in [self.id_, self.age, self.gender, self.atRisk, self.role, self.home, self.work,
                                 self.visitFreqs['home'], self.visitFreqs['school'], self.visitFreqs['office'],
                                 self.visitFreqs['sport'], self.visitFreqs['super'], self.visitFreqs['store'],
                                 self.visitFreqs['restaurant'],
                                 self.favPlaces['home'][0], self.favPlaces['home'][1],
                                 self.favPlaces['school'][0], self.favPlaces['school'][1],
                                 self.favPlaces['office'][0], self.favPlaces['office'][1],
                                 self.favPlaces['sport'][0], self.favPlaces['sport'][1],
                                 self.favPlaces['super'][0], self.favPlaces['super'][1],
                                 self.favPlaces['store'][0], self.favPlaces['store'][1],
                                 self.favPlaces['restaurant'][0], self.favPlaces['restaurant'][1]] if v is not None]


class Encounter:
    def __init__(self, pid1=None, pid2=None, placeName=None, placeType=None, lat=None, lon=None, time=None):
        self.pid1 = pid1
        self.pid2 = pid2
        self.placeName = placeName
        self.placeType = placeType
        self.lat = lat
        self.lon = lon
        self.time = time

    def __str__(self):
        return f"Encounter: {self.listOfStrings()}"

    __repr__ = __str__

    def listOfStrings(self):
        return [f"{v}" for v in [self.pid1, self.pid2, self.placeName, self.placeType, self.lat, self.lon,
                                 self.time.strftime('%Y-%m-%d %H:%M:%S') if self.time is not None else None]
                if v is not None]


class AggregatedEncounter:
    def __init__(self, placeType=None, lat=None, lon=None, time=None, age=None, gender=None, atRisk=None, role=None):
        self.placeType = placeType
        self.lat = lat
        self.lon = lon
        self.time = time
        self.age = age
        self.gender = gender
        self.atRisk = atRisk
        self.role = role

    def __str__(self):
        return f"AggregatedEncounter: {self.listOfStrings()}"

    __repr__ = __str__

    def listOfStrings(self):
        return [f"{v}" for v in [self.placeType, self.lat, self.lon,
                                 self.time.strftime('%Y-%m-%d %H:%M:%S') if self.time is not None else None,
                                 self.age, self.gender, self.atRisk, self.role] if v is not None]


class Symptom:
    @staticmethod
    def sqlDropTable(tableName='symptoms'):
        return f"DROP TABLE IF EXISTS {tableName};"

    def __init__(self, pid=None, time=None):
        self.pid = pid
        self.time = time

    def __str__(self):
        return f"Symptom: {self.listOfStrings()}"

    __repr__ = __str__

    def listOfStrings(self):
        return [f"{v}" for v in [self.pid, self.time] if v is not None]

    def sqlCreateTable(self, tableName='symptoms'):
        sql = f"CREATE TABLE IF NOT EXISTS {tableName}("
        notNone = [s for v, s in [(self.pid, 'pid text'), (self.time, 'time datetime')] if v is not None]
        for i in range(len(notNone)):
            sql += f"{notNone[i]}"
            if i < len(notNone) - 1:
                sql += f","
        sql += f");"
        return sql

    def sqlInsertInto(self, tableName='symptoms'):
        sql = f"INSERT INTO {tableName} VALUES("
        notNone = [s for s in [f"'{self.pid}'" if self.pid is not None else None,
                               f"'{self.time.strftime('%Y-%m-%d %H:%M:%S')}'" if self.time is not None else None]
                   if s is not None]
        for i in range(len(notNone)):
            sql += f"{notNone[i]}"
            if i < len(notNone) - 1:
                sql += f","
        sql += f");"
        return sql
