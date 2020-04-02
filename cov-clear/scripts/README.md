# cov-clear scripts

## makeSqlFromCsv.py

Takes as input the csv file provided by cov-clear and generates
a file called 'sql.txt' which is a list of sql commands. The
commands create and populate three tables, a 'survey' table, a
'symptoms' table, and a 'questions' table. 

### Inputs

* `colInfo.json`: the configuration. `colInfo.json` assigns short
column names to survey questions. It also indicates when special
handling of data is required.
* `<originalData>.csv`: The csv file from cov-clear.

### Outputs

* `sql.txt`: The sql commands needed to populate all three tables.
* `colDifferences.json`: If `<originalData>.csv` doesn't match the configuration in `colInfo.json`, then `colDifferences.json` is produced and the program aborts.
* `characterize.json`: This is formatted like `colInfo.json`, but lists up to 10 distinct column values for each column. This is produces by setting the `justCharacterize` flag to `True` in the `getColInfo` class object creation call. Can contain sensitive information.
* `colsAndQuestions.csv`: The column names and questions, sorted by column name

### Features

* Converts 'Day dd Month' to postgres date
* Converts 'dd/mm/yyyy hh:mm' to postgres timestamp
* Puts postcodes in upper case and removes spaces
* Populates the symptoms table with columns labeled `"specialHandling":"symptom"`
* Uses the postal code and country name to generate three new columns: `country_code`, `lat`, and `long`.

### Limitations

* Currently 'Day dd Month' strings are assumed to be 2020

## postalLatLong.py

Used to map country and post code into lat and long

### Data sources:
* https://data.opendatasoft.com/explore/dataset/geonames-postal-code
  * exported as json into geonames-postal-code.json
  * licensed as https://creativecommons.org/licenses/by/4.0/
* table of country name to country code 
  * countryCodes.json
  * (I forget where I got it)

From above two data sources, builds sqlite table with columns:
* `admin_code,accuracy,admin_name,cc,country,lat,long,post`
  * cc is country code
  * country is country name
  * lat is latitude (decimal format)
  * long is longitude (decimal format)
  * post is post code / zip code

### What it does

* On init, generates the database if force=True or if the database doesn't already exist (geonames.db)

Exposes the following API:
* getCC(country): returns country code from country name
  * works only on exact match
* getLatLong(cc,zipCode): returns lat and long from country
  * code and post/zip code
  * Searches for best match (longest zip code prefix)
  * Selects randomly if multiple lat/long matches

## makeQuestionsCsv.py

Produces `colsAndQuestions.csv`, which contains the column names and
associated questions, sorted alphabetically by column name.

### To run

Can be run standalone (`python makeQuestionsCsv.py`)
Is called by makeSqlFromCsv.py

## Other Files

* `colInfo.json`: Config for `makeSqlFromCsv.py`
* `countryCodes.json`: Used by `postalLatLong.py`
* `cov_clear.json`: This is the Aircloak Insights cloak configuration file
* `colsAndQuestions.csv`: column names and questions, sorted by column name
