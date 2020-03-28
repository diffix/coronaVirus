# cov-clear scripts

## makeSqlFromCsv.py

Takes as input the csv file provided by cov-clear and generates
a file called 'sql.txt' which is a list of sql commands. The
commands create and populate two tables, a 'questions' table and
a 'survey' table. 

The 'survey' table contains all of the survey results.

The 'questions' table simply maps the column names of the 'survey'
table to the original survey questions.
