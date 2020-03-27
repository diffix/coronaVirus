import csv
import json

'''
Takes as input the csv file provided by cov-clear and puts the
column questions into a json file colNameTemplate.json so that
one can manually edit the file to associate succinct columns names
with each question.
'''

fileName = '20200327 1053 Export.csv'

columnNames = []
with open(fileName, newline='') as csvfile:
    lines = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in lines:
        for item in row:
            columnNames.append(['xx',item])
        break

with open("colNameTemplate.json", 'w') as fo:
    json.dump(columnNames,fo,indent=4)
