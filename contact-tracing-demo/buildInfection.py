import os.path
from common import ElapsedTimer
from dataAccess import DataAccess
from infection import Infection


timer = ElapsedTimer()
timer.start()

print(f"| Loading data")
dataAccess = DataAccess(os.path.join('out', 'prox.db'))
encounters = dataAccess.loadEncounters()
totalLoaded = len(encounters)
print(f"|    Loaded {totalLoaded} encounters from database.")
people = dataAccess.loadPeople()
print(f"|    Loaded {len(people)} people from database.")
timer.printElapsed()

startRole = 'student'
symptoms = Infection.infect(encounters, people=people, startRole=startRole)
print(f"|       Obtained {len(symptoms)} symptom events.")
timer.printElapsed()

print(f"| Saving symptoms to database")
dataAccess.saveToTable(symptoms)
timer.printElapsed()

timer.finish()
