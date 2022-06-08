import datetime
import os.path
from aggregation import Aggregator
from common import ElapsedTimer
from dataAccess import DataAccess, AggregatedEncounter


minDistinct = 10

timeBegin = datetime.datetime(year=2020, month=4, day=15)
latBegin = 49.42
lonBegin = 7.72
ageBegin = 0

timer = ElapsedTimer()
timer.start()

print(f"| Loading data")
dataAccess = DataAccess(os.path.join('out', 'prox.db'))
encounters = [(e, AggregatedEncounter()) for e in dataAccess.loadEncounters()]
totalLoaded = len(encounters)
print(f"|    Loaded {totalLoaded} encounters from database.")
people = dataAccess.loadPeople()
print(f"|    Loaded {len(people)} people from database.")
timer.printElapsed()

print(f"| 1) Aggregation of time and location")
timeDelta = datetime.timedelta(hours=1)
latDelta = 0.005  # ~555m
lonDelta = 0.007  # ~555m (at 45 degrees)

tmpEncounters = encounters.copy()

print(f"|    Time aggregation with bucket size {timeDelta}.")
bucketizations = Aggregator.aggregateTime(tmpEncounters, timeBegin, timeDelta)
print(f"|    Location aggregation with bucket size {latDelta}, {lonDelta}.")
bucketizations.extend(Aggregator.aggregateLocation(tmpEncounters, latBegin, latDelta, lonBegin, lonDelta))
timer.printElapsed()

print(f"|    Low count filter buckets with less than {minDistinct} distinct people.")
tmpEncounters = Aggregator.lowCount(tmpEncounters, bucketizations, minDistinct)
print(f"|       Obtained {len(tmpEncounters)} ({len(tmpEncounters) / totalLoaded * 100:.1f}%) aggregated encounters.")
timer.printElapsed()

csvPath = os.path.join('out', 'agg_enc_1.csv')
print(f"|    Saving aggregated encounters to {csvPath}.")
dataAccess.writeToCsv(csvPath, map(lambda ea: ea[1], tmpEncounters))
print(f"|       Saved {len(tmpEncounters)} aggregated encounters to {csvPath}.")
timer.printElapsed()

print(f"| 2) Aggregation of time, location, and age")
timeDelta = datetime.timedelta(hours=2)
latDelta = 0.01  # ~1110m
lonDelta = 0.014  # ~1110m (at 45 degrees)
ageDelta = 20

tmpEncounters = encounters.copy()

print(f"|    Time aggregation with bucket size {timeDelta}.")
bucketizations = Aggregator.aggregateTime(tmpEncounters, timeBegin, timeDelta)
print(f"|    Location aggregation with bucket size {latDelta}, {lonDelta}.")
bucketizations.extend(Aggregator.aggregateLocation(tmpEncounters, latBegin, latDelta, lonBegin, lonDelta))
print(f"|    Age aggregation with bucket size {ageDelta}.")
bucketizations.extend(Aggregator.aggregateAge(tmpEncounters, people, ageBegin, ageDelta))
timer.printElapsed()

print(f"|    Low count filter buckets with less than {minDistinct} distinct people.")
tmpEncounters = Aggregator.lowCount(tmpEncounters, bucketizations, minDistinct, people=people)
print(f"|       Obtained {len(tmpEncounters)} ({len(tmpEncounters) / totalLoaded * 100:.1f}%) aggregated encounters.")
timer.printElapsed()

csvPath = os.path.join('out', 'agg_enc_2.csv')
print(f"|    Saving aggregated encounters to {csvPath}.")
dataAccess.writeToCsv(csvPath, map(lambda ea: ea[1], tmpEncounters))
print(f"|       Saved {len(tmpEncounters)} aggregated encounters to {csvPath}.")
timer.printElapsed()

print(f"| 3) Aggregation of time, location, and atRisk")
timeDelta = datetime.timedelta(hours=3)
latDelta = 0.01  # ~1110m
lonDelta = 0.014  # ~1110m (at 45 degrees)

tmpEncounters = encounters.copy()

print(f"|    Time aggregation with bucket size {timeDelta}.")
bucketizations = Aggregator.aggregateTime(tmpEncounters, timeBegin, timeDelta)
print(f"|    Location aggregation with bucket size {latDelta}, {lonDelta}.")
bucketizations.extend(Aggregator.aggregateLocation(tmpEncounters, latBegin, latDelta, lonBegin, lonDelta))
print(f"|    AtRisk aggregation.")
bucketizations.extend(Aggregator.aggregateAtRisk(tmpEncounters, people))
timer.printElapsed()

print(f"|    Low count filter buckets with less than {minDistinct} distinct people.")
tmpEncounters = Aggregator.lowCount(tmpEncounters, bucketizations, minDistinct, people=people)
print(f"|       Obtained {len(tmpEncounters)} ({len(tmpEncounters) / totalLoaded * 100:.1f}%) aggregated encounters.")
timer.printElapsed()

csvPath = os.path.join('out', 'agg_enc_3.csv')
print(f"|    Saving aggregated encounters to {csvPath}.")
dataAccess.writeToCsv(csvPath, map(lambda ea: ea[1], tmpEncounters))
print(f"|       Saved {len(tmpEncounters)} aggregated encounters to {csvPath}.")
timer.printElapsed()

timer.finish()
