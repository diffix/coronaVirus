import os
import os.path
import sys
import pprint
import random
import sqlite3
import hashlib
import secrets
import psycopg2
from datetime import datetime,timedelta
from person import Person
from encounter import Encounter

'''
This generates the dataset to be used by Aircloak from the dataset that is
stored locally in sqlite. There are three tables, 'people', 'encounters', and
'stats'. (work on 'stats' later)
  * 'people' has demographic info (age, etc.)
  * 'encounters' has each encounter
  * 'stats' has other encounter-related information, aggregated per person
linked by 'pid'.
Some things this does:
  * Generates two rows for every encounter, where both pid1 and pid2 are used
    for one row each. (Change column name pid1 --> pid)
    * pid here is the cloak user_id
  * pid2 will be given a different encoding for each person. Specifically, pid2
    is based on a hash of pid1 and pid2. This allows one to learn things about for
    instance how many different persons each pid encounters, but without having to
    protect the pid2 value as a user_id.
'''

buildDb = True
pp = pprint.PrettyPrinter(indent=2)

class MakeEncounter:
    def __init__(self):
        # these are the column indices for encounters:
        encParams = Encounter.getTableIndices()
        self.pid1 = encParams['pid1']
        self.pid2 = encParams['pid2']
        self.place = encParams['place_name']
        self.time = encParams['time']
        self.lat = encParams['lat']
        self.lon = encParams['lon']
        # these are the column indices for people (from sqlite)
        peopleParams = Person.getTableIndices()
        self.pid = peopleParams['pid']
        self.age = peopleParams['age']
        self.gender = peopleParams['gender']
        self.at_risk = peopleParams['at_risk']
        self.role = peopleParams['role']
        self.home = peopleParams['home']

        self.pids = [self.pid1,self.pid2]
        self.minLat = 49.423043
        self.maxLat = 49.454434
        self.minLon = 7.726833
        self.maxLon = 7.808753
        self.locErr = .00005
        self.timeErr = 10     # seconds, in each direction
        self.locs = {}
        self.distinct = {}
        self.totalEnc = {}
        self.people = {}
        self.secret = secrets.token_hex(16)

    def putPeopleHome(self,per):
        if per[self.pid] in self.people:
            print(f"Error duplicate people id {per[self.pid]}")
            quit()
        self.people[per[self.pid]] = per[self.home]
        return

    def getPeopleHome(self,pid):
        return self.people[pid]

    def make(self,en,p1,p2):
        '''
            Creates a single row for the encounter table.
            fid: family id, to be used as cloak user_id
            pid: person id
            pid2: ID of the other person in the encounter, hashed so that it
                is unique to the pid
            first: set to 1 if this is the first encounter with pid2 today, else 0
                this allows us to look at distinct encounters per day
            dt: time of encounter in python datetime format (for sorting later)
            lat/lon/time/place/: self explanatory
        '''
        # The following lets me treat either pid1 or pid2 as the user_id pid
        pidIdx = self.pids[p1]
        pid2Idx = self.pids[p2]
        pid = en[pidIdx]
        pid2 = en[pid2Idx]
        key = pid+pid2
        first = 1
        if key in self.distinct:
            self.distinct[key] += 1
            first = 0
        else:
            self.distinct[key] = 0
        # The following is only to identify the person with the max encounters
        # so as to color later
        if pid in self.totalEnc:
            self.totalEnc[pid] += 1
        else:
            self.totalEnc[pid] = 1
        thing = bytes(str(f"{pid}{pid2}{self.secret}"),'utf-8')
        new_pid2 = hashlib.sha224(thing).hexdigest()
        home = self.getPeopleHome(pid)
        thing = bytes(str(f"{home}{self.secret}"),'utf-8')
        fid = hashlib.sha224(thing).hexdigest()
        lat = en[self.lat]
        lat += (random.random() * self.locErr) - self.locErr/2
        lon = en[self.lon]
        lon += (random.random() * self.locErr) - self.locErr/2
        dtIn = datetime.fromisoformat(en[self.time])
        errorSecs = int(round((random.random() * self.timeErr) - self.timeErr/2))
        dtEvent = dtIn + timedelta(seconds=errorSecs)
        return {'fid':fid,'pid':pid,'pid2':new_pid2,'first':first,'lat':lat,'lon':lon,'time':str(dtEvent),'place':en[self.place],'dt':dtEvent}

    def getEncParams(self,en):
        self.peopleParams = Person.getTableIndices()
        return(en['fid'],en['pid'],en['pid2'],en['lat'],en['lon'],en['time'],en['place'],en['dt'],en['first'])

    def getPeopleParams(self,row):
        return(row[self.pid],row[self.age],row[self.gender],row[self.at_risk],row[self.role])

    def orderByTime(self,encounters):
        encounters.sort(key=lambda item:item['dt'])
        return encounters

    def getMaxPerson(self):
        maxPerson = ''
        maxEncounters = 0
        for pid, val in self.totalEnc.items():
            if val > maxEncounters:
                maxEncounters = val
                maxPerson = pid
        return(maxPerson,maxEncounters)

    def ranLocs(self,places):
        latRange = self.maxLat - self.minLat
        lonRange = self.maxLon - self.minLon
        for pl in places:
            lat = (random.random() * latRange) + self.minLat
            lon = (random.random() * lonRange) + self.minLon
            self.locs[pl[0]] = (lat,lon)

    def printLocs(self):
        pp.pprint(self.locs)

def getQuery(cur,sql):
    cur.execute(sql)
    return(cur.fetchall())

updateDb = False
assignRanLoc = False

if len(sys.argv) > 1:
    outName = sys.argv[1]
else:
    outName = 'prox'

# Get people and encounters data
dbDir = os.path.join('out')
dbPath = os.path.join('out',outName+'.db')
conn = sqlite3.connect(dbPath)
cur = conn.cursor()
sql = '''select * from people'''
people = getQuery(cur,sql)
# Before I was ignoring night encounters, but proxEncounters.py fixed to have fewer
# night encounters, so should be ok now
#sql = "SELECT * FROM encounters where cast(strftime('%H', time) as integer) between 6 and 22"
sql = ''' select * from encounters '''
encounters = getQuery(cur,sql)
if assignRanLoc:
    # Needed to assign random lat/lon
    sql = 'SELECT distinct place_name FROM encounters'
    places = getQuery(cur,sql)
conn.close()

me = MakeEncounter()
if assignRanLoc:
    me.ranLocs(places)
    # For now, assign a random lat/lon to each place

for per in people:
    # This is for the purpose of assigning fid (as uid)
    me.putPeopleHome(per)

enCols = ['pid','pid2','time','lat','lon']
cloakEn = []

for en in encounters:
    thing = me.make(en,0,1)
    if thing:
        cloakEn.append(thing)
    thing = me.make(en,1,0)
    if thing:
        cloakEn.append(thing)

print(f"{len(cloakEn)} entries")
pp.pprint(cloakEn[:5])

(maxPid,numEncounters) = me.getMaxPerson()
print(f"Person {maxPid} has the most encounters with {numEncounters}")

cloakEn = me.orderByTime(cloakEn)
print(f"{len(cloakEn)} entries ordered")

if False:
    # Let's make a csv file for Jakob
    fo = open('out.csv','w',encoding='utf-8')
    fo.write("lat,lon,time,color\n")
    for en in cloakEn:
        (fid,pid,pid2,lat,lon,time,place,td,first) = me.getEncParams(en)
        if pid == maxPid:
            color = 'c2'
        else:
            color = 'c1'
        fo.write(f"{lat},{lon},{time},{color}\n")
    fo.close()

host = 'vrt-20-0101.mpi-sws.org'
port = 5432
dbname = 'corona'
user = 'corona'
env = os.environ.get('CORONA_DB_PW')
if env is not None:
    password = env
else:
    print(f"environ didn't work")
    quit()

connStr = str(
    f"host={host} port={port} dbname={dbname} user={user} password={password}")
if buildDb: conn = psycopg2.connect(connStr)
if buildDb: cur = conn.cursor()
print(f"Connected to {host}")

# Let's start by building the people table. This can be joined with the
# encounters table on pid
pTab = 'people_' + outName
sql = f'''DROP TABLE IF EXISTS {pTab} CASCADE;'''
if buildDb: cur.execute(sql)
print(sql)
if buildDb: conn.commit()
sql = f'''CREATE TABLE IF NOT EXISTS {pTab} (
        pid text,
        age integer,
        gender text,
        at_risk integer,
        role text
    );'''
if buildDb: cur.execute(sql)
print(sql)
if buildDb: conn.commit()

sql = ''
for row in people:
    (pid, age, gender, at_risk, role) = me.getPeopleParams(row)
    sql += f'''
INSERT INTO {pTab} VALUES (
    '{pid}',
    {age},
    '{gender}',
    {at_risk},
    '{role}'
); 
    '''
cur.execute(sql)
conn.commit()

# Now let's build the encounters table
encTab = 'encounters_' + outName

sql = f'''DROP TABLE IF EXISTS {encTab} CASCADE;'''
if buildDb: cur.execute(sql)
print(sql)
if buildDb: conn.commit()
sql = f'''CREATE TABLE IF NOT EXISTS {encTab} (
        fid text,
        pid text,
        pid2 text,
        lat real,
        lon real,
        place text,
        time timestamp,
        epoch integer,
        first integer
    );'''
if buildDb: cur.execute(sql)
print(sql)
if buildDb: conn.commit()

numRows = 0
sql = ''
for en in cloakEn:
    (fid,pid,pid2,lat,lon,time,place,td,first) = me.getEncParams(en)
    epoch = int(td.timestamp())
    sql += f'''
INSERT INTO {encTab} VALUES (
    '{fid}',
    '{pid}',
    '{pid2}',
    {lat},
    {lon},
    '{place}',
    '{time}',
    {epoch},
    {first}
); 
    '''
    numRows += 1
    if numRows % 10000 == 0:
        print(f"{numRows} of {len(cloakEn)}")
        if buildDb:
            cur.execute(sql)
        sql = ''
if len(sql) > 1:
    if buildDb:
        cur.execute(sql)
    else:
        #print(sql)
        pass
if buildDb: conn.commit()
if buildDb: conn.close()

