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
