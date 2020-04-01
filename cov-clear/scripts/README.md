# cov-clear scripts

## makeSqlFromCsv.py

Takes as input the csv file provided by cov-clear and generates
a file called 'sql.txt' which is a list of sql commands. The
commands create and populate two tables, a 'questions' table and
a 'survey' table. 

The 'survey' table contains all of the survey results.

The 'questions' table simply maps the column names of the 'survey'
table to the original survey questions.

### Features

makeSqlFromCsv.py does the following:

* Automatically chooses short column names (the column names in the original csv file are the actual questions).
* Automatically detects column type (text, real, int, date, timestamp)
* Converts 'Day dd Month' to postgres date
* Converts 'dd/mm/yyyy hh:mm' to postgres timestamp
* Puts postcodes in upper case and removes spaces

### Limitations

* Currently 'Day dd Month' strings are assumed to be 2020
* Automatically choosing column names probably a bad idea, because a small change in the question might lead to a new column name

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

