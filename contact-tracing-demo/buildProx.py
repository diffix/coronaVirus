import datetime
import os.path
import pprint
import sqlite3
import sys
from common import ElapsedTimer
from datetime import timedelta
from policy import Policy
from encounter import Encounter
from person import Person
from place import Place, PlaceAddressTracker
from simulation import Simulation
from statistic import Statistic


timer = ElapsedTimer()
timer.start()

pp = pprint.PrettyPrinter(indent=2)

if len(sys.argv) > 1:
    numPeople = int(sys.argv[1])
else:
    #numPeople = 96340  # Kaiserslautern: 96340  # 1000-->1.5s 10000-->15s 100000-->365s
    numPeople = 1000
if len(sys.argv) > 2:
    numDays = int(sys.argv[2])
else:
    numDays = 1
if len(sys.argv) > 3:
    outName = sys.argv[3]
else:
    outName = 'prox'


# Actual date doesn't matter, so we just pick this arbitrarily
startDate = datetime.datetime(2020, 4, 15).date()

# Set up sql connector (db located in directory 'out')
dbDir = os.path.join('out')
if not os.path.exists(dbDir):
    os.mkdir(dbDir)
dbPath = os.path.join('out', outName+'.db')
conn = sqlite3.connect(dbPath)
cur = conn.cursor()

print(f"Build simulation with {numPeople} people over {numDays} days\n")

timer.printElapsed()
print('''
Phase 0: Create homes for a number of people.
* Different types of homes, e.g., two adults with single child, follow a provided distribution.
        ''')
addressPath = os.path.join('maps', 'openstreetmap_location_data.json')
placeAddressTracker = PlaceAddressTracker.loadAddresses(addressPath)
homes = Place.generateHomes(numPeople, placeAddressTracker)
Place.populateHomesDb(homes, cur, conn)

timer.printElapsed()
print('''
Phase 1: Create the people.
* Each person has age, gender, and frequency with which it visits
  each type of place
        ''')
people = Person.generatePeople(homes)

timer.printElapsed()
print('''
Phase 2: Build places to work and visit.
* Each person has either a work place or stays at home
  * people over 80 or under 5 stay at home
  * people between 5 and 20 go to school
  * people between 20 and 60, 80% work and 20% stay at home
At this point, people only have a single frequency for a single type of place.
* Each person may have a frequent place of each type (place that the person
  tends to go when visiting that type of place)
* Each person may a second frequent place (second choice place).
* As we assign visitors to places, we keep in mind the capacity of the
  place, and if capacity is exceeded, we make a new place
* In this way, the number of people determines the number of places
        ''')
workPlaces = Place.generateWorkPlaces(people, placeAddressTracker)
placeAddressTracker.printStats()
Place.populateWorkPlacesDb(workPlaces, cur, conn)

timer.printElapsed()
print('''
Phase 3: Assign people to work/home/school places
At this point, we create enough places up front and do not create more places during assignment.
* The places to visit count also as work places, so users can be assigned
  to the existing places as work places
* Keeping the capacity of the school or work place in mind, more schools or
  offices can be created to assign more work places.
        ''')
Person.assignWorkPlaces(people, workPlaces)

timer.printElapsed()
print('''
Phase 3.5: Assign favorite places to people. Each person gets a favorite place and
a second favorite place of each place type. They visit the favorite places with
higher probability than other places.
        ''')
Person.assignFavorites(people, workPlaces, homes)
Person.populatePeopleDb(people, cur, conn)

timer.printElapsed()
print('''
Phase 4: Go through time, and assign people to places, and encounters
between people.
* By default, people are at work, school, or home
* If not at work or school, then home
* From this default, people visit places. In other words, they can visit
  a place from home or work. (We force students to stay in school!)
* Once a person is visiting a place, they cannot visit another place until
  they are done
* Then, among the people that are visiting a place, we assign encounters
  according to the likely number of encounters the person can be expected
  to have there
        ''')

"""
Simulation requires a policy. The default normal has all places open. The default restrictive tries to mimic German
lock-down rules. For instance, schools offer emergency care for essential workers' kids. Thus, even in lock-down 1% of
kids will go to "work" at their school.
"""
policy = Policy.defaultNormal(people, homes, workPlaces)

for i in range(numDays):
    if i == 1:
        policy.closePlaces('office', keepOpen=0.2)
    if i == 2:
        policy.closePlaces('school')
    if i == 3:
        policy.closePlaces('sport')
        policy.closePlaces('restaurant')
        policy.closePlaces('store', keepOpen=0.5)
    if i == 4:
        policy.openPlaces('restaurant', keepClosed=0.5)
        policy.openPlaces('store', keepClosed=0.2)
        policy.openPlaces('office', keepClosed=0.5)

    visits = Simulation.generateVisits(startDate, 1, policy)
    if i == 0:
        Statistic.printStatistics(visits)
    encounters = Encounter.generateEncountersDay(visits)
    startDate = startDate + timedelta(days=1)
    if i == 0:
        Simulation.populateVisitsDb(visits, cur, conn, flush=True)
        Encounter.populateEncountersDb(encounters, cur, conn, flush=True)
    else:
        Simulation.populateVisitsDb(visits, cur, conn, flush=False)
        Encounter.populateEncountersDb(encounters, cur, conn, flush=False)

conn.close()

timer.printElapsed()
timer.finish()
