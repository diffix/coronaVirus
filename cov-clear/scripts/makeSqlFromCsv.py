import nltk
from nltk.corpus import brown
from nltk.probability import ConditionalFreqDist
from nltk.tokenize import word_tokenize
import re
import csv
import json
import pprint
import os.path

pp = pprint.PrettyPrinter(indent=4)

'''
Takes as input the csv file provided by cov-clear and generates
a file called 'sql.txt' which is a list of sql commands. The
commands create and populate two tables, a 'questions' table and
a 'survey' table. 

The 'survey' table contains all of the survey results.

The 'questions' table simply maps the column names of the 'survey'
table to the original survey questions.
'''

class weighTerms:
    cfdist = None

    def __init__(self):
        self.cfdist = ConditionalFreqDist()
        for sentence in brown.sents():
            for word in sentence:
                condition = len(word)
                self.cfdist[condition][word] += 1
        return

    def getFreq(self,word):
        return self.cfdist[len(word)].freq(word)

    def getBestTerms(self,phrase,numTerms=2):
        stoppers = ['coronavirus','utc']
        terms = phrase.split()
        bestTerms = []
        for term in terms:
            term = term.lower()
            term = re.sub(r'\W+', '', term)
            if term in stoppers:
                continue
            if len(term) < 2:
                continue
            bestTerms.append([term.lower(),self.getFreq(term)])
        bestTerms = sorted(bestTerms, key=lambda t: t[1])
        ret = []
        for i in range(numTerms):
            if i > (len(bestTerms)-1):
                break
            ret.append(bestTerms[i][0])
        return(ret)

def is_int(val):
    try:
        int(val)
        return True
    except ValueError:
        return False

def is_float(val):
    try:
        float(val)
        return True
    except ValueError:
        return False

def getDateFromVal(val):
    # If val is 'Day dd Month', generate a correctly formatted date
    # otherwise return None
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul',
            'Aug','Sep','Oct','Nov','Dec']
    mons = ['01','02','03','04','05','06','07','08','09','10','11','12']
    days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    terms = val.split()
    if len(terms) == 3 and terms[0][:3] in days and terms[2][:3] in months:
        month = mons[months.index(terms[2][:3])]
        day = terms[1]
        return str(f"2020-{month}-{day}")
    return None

def getColInfo(firstLine,allLines):
    wt = weighTerms()
    # Assign terse column names to each column
    colNames = []
    colInfo = [None] * len(firstLine)
    for i in range(len(firstLine)):
        if i == 0:
            # special case of uid
            colInfo[i] = {'phrase':'uid','colName':'uid'}
            continue
        phrase = firstLine[i]
        bestTerms = wt.getBestTerms(phrase)
        colName = '_'.join(bestTerms)
        if colName in colNames:
            bestTerms = wt.getBestTerms(phrase,numTerms=3)
            colName = '_'.join(bestTerms)
            if colName in colNames:
                orig = colName
                cnt = 1
                while True:
                    colName = orig + '_' + str(cnt)
                    if colName not in colNames:
                        break
        colInfo[i] = {'phrase':phrase,'colName':colName}
        colNames.append(colName)
    
    # To colInfo we want to add the column type
    for i in range(len(colInfo)):
        if 'type' in colInfo[i] and colInfo[i]['type'] == 'date':
            # Sometimes a date field also has non-date text, so
            # once the field is established as date, we stick to that
            continue
        for row in allLines:
            val = row[i]
            # datetime in the system is 'dd/mm/yyyy hh:mm'
            if len(val) == 16 and val[2] == '/' and val[13] == ':':
                colInfo[i]['type'] = 'timestamp without time zone'
                break
            elif re.search('[a-zA-Z]', val):
                # Some kind of text
                # Some date fields look like 'Day dd Month'
                if getDateFromVal(val):
                    colInfo[i]['type'] = 'date'
                else:
                    colInfo[i]['type'] = 'text'
                break
            elif is_int(val):
                # tentatively assign as integer
                if 'type' not in colInfo[i]:
                    colInfo[i]['type'] = 'int'
            elif is_float(val):
                # tentatively assign as a real
                colInfo[i]['type'] = 'real'
        if 'type' not in colInfo[i]:
            colInfo[i]['type'] = 'text'
    return colInfo

def addVal(ci,val):
    if len(val) == 0:
        return "NULL"
    if ci['type'] == 'text':
        new = val.replace("'","''")
        if ci['colName'].find('post') >= 0 or ci['colName'].find('zip') >= 0:
            # This is a small attempt at making the zip codes uniform.
            # We force upper case and remove spaces
            new = new.upper()
            new = new.replace(' ','')
        return str(f"'{new}'")
    elif ci['type'] == 'timestamp without time zone':
        (date,time) = val.split()
        (day,mon,year) = date.split('/')
        (hour,minute) = time.split(':')
        return str(f"'{year}-{mon}-{day} {hour}:{minute}:00'")
    elif ci['type'] == 'date':
        new = getDateFromVal(val)
        if new is None:
            return "NULL"
        else:
            return str(f"'{new}'")
    else:
        return str(f"{val}")

csvName = '20200327 1053 Export.csv'
colInfoFile = 'colInfo.json'

# Read in and store csv file
allLines = []
firstLine = None
with open(csvName, encoding='utf8',newline='') as csvfile:
    lines = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in lines:
        if firstLine is None:
            firstLine = row
        else:
            allLines.append(row)

if os.path.isfile(colInfoFile):
    with open(colInfoFile, 'r') as fi:
        colInfo = json.load(fi)
else:
    colInfo = getColInfo(firstLine,allLines)
    with open(colInfoFile, 'w') as fo:
        json.dump(colInfo,fo,indent=4)

# Now we have column name and type.

# We want to build two tables. One is a non-personal table that maps
# the column name to the question asked. The other is the survey table.

fo = open("sql.txt", 'w', encoding='utf8')

# Start with questions table.
fo.write('DROP TABLE IF EXISTS questions;\n')
sql = '''CREATE TABLE IF NOT EXISTS questions (
    column_name text, question text);\n
'''
fo.write(sql)
for entry in colInfo:
    sql = str(f"INSERT INTO questions VALUES('{entry['colName']}', ")
    # need to escape the single quotes in the question phrase
    new = entry['phrase'].replace("'","''")
    sql += str(f"'{new}');\n")
    fo.write(sql)

# And then survey table
fo.write('DROP TABLE IF EXISTS survey;\n')
sql = 'CREATE TABLE IF NOT EXISTS survey ('
for entry in colInfo:
    sql += str(f"{entry['colName']} {entry['type']}, ")
sql = sql[:-2]
sql += ');\n'
fo.write(sql)
for row in allLines:
    sql = "INSERT INTO survey VALUES( "
    for i in range(len(row)):
        sql += addVal(colInfo[i],row[i]) + ", "
    sql = sql[:-2]
    sql += ");\n"
    fo.write(sql)

#pp.pprint(colInfo)
fo.close()
