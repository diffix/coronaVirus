# syn-proximity-data-gen

Project to build synthetic data that mimics contact tracing data.

Assumes a tool that can correlate location and contacts. Unfortunately this is not something current Apple/Google tool can do, so this tool is maybe limited value.

As of this writing, the tool is designed to mimic what would happen if different lockdown policies were in place. There are by default 5 policies specified that each get implemented for one day. This can be edited in `buildProx.py`. Look for `policy`.

Currently runs over Kaiserslautern. To make this work for another town, would have to do some work in the `maps` directory.

## Setup

Put paths to `src`, `src/aggregation` and `src/prox` in `PYTHONPATH`.

## To run

### Build trace of encounters

`python buildProx.py numPersons numDays outName`

* numPersons is the number of people in the dataset (default 1000)
* numDays is the number of days the simulation populates (default 1)
* outName is the name of the output files (default 'prox')

To run the full 5-day simulation with say 50K people (half of Kaiserslautern's population), you'd do `python buildProx.py 50000 5`.

This builds the traces and generates the output, which is stored in `out/outName.db` (sqlite3 db).

This output consists of five tables:

* `encounters`: each row is a contact (encounter) between two persons at a lat/lon and time.
* `people`: each row is one person, with some demographics and a lot of information pertinant to the simulation itself.
* `homes`: data about each home (for simulation / debugging), including lat/lon of the home.
* `visits`: each row is a start and end time of a person to a place.
* `workPlaces`: data about each workPlace (places other than homes), including lat/lon of the work place.

### View statistics about the encounters (optional, good for debugging)

`python seeProx.py outName > outfile`

Executes a set of queries over tables in `outName.db` and prints out the answers.

### Convert data to something suitable for Aircloak

The data in the `encounters` and `people` tables in `outName.db` is converted to something suitable for Aircloak:

1. It takes `pid2` (one of the two person IDs in an encounter) and modifies it to be unique to `pid1` (essentially a secure hash of `<pid1,pid2,secret>`). This necessary because aircloak cannot protect records with two records.
2. It assigns a "family id" (`fid`) to all persons that share a home. This is used as the protected `user_id` in Aircloak.
3. It adds a little noise to the place lat/lon so that all lat/lon values for a given place aren't the same.

It then builds a table and populates a database with the table. This database becomes the data source. 

#### Config

The environment variable `CORONA_DB_PW` must be configured with the password for the database specified in proxData.py. 

#### To run

`python proxData.py outName`, where `outName` causes the data to come from `out/outName.db`
