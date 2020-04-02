import nltk
from nltk.corpus import brown
from nltk.probability import ConditionalFreqDist
from nltk.tokenize import word_tokenize
from postalLatLong import postalLatLong
from makeQuestionsCsv import colsQuestions
import random
import re
import csv
import json
import pprint
import os.path

pp = pprint.PrettyPrinter(indent=4)

'''
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

class getColInfo:
    colInfoFile = 'colInfo.json'
    colDifferencesFile = 'colDifferences.json'
    characterizeFile = 'characterize.json'
    colInfo = None
    colInfoNew = None
    postIndex = None
    countryIndex = None
    emailIndex = None
    justCharacterize = False
    allLines = None

    def __init__(self,firstLine,allLines,justCharacterize=False):
        # Get existing colInfo file
        self.allLines = allLines
        self.justCharacterize = justCharacterize
        if os.path.isfile(self.colInfoFile):
            fi = open(self.colInfoFile, 'r')
            self.colInfo = json.load(fi)
            fi.close()
        else:
            print(f"Couldn't find file {colInfoFile}....abort")
            quit()
        # Generate the columns/questions csv file
        colsQuestions(self.colInfo)
        # Get any new column info
        self.colInfoNew = self._getColInfo(firstLine,allLines)
        (differences,characterize) = self._characterize()
        if len(characterize) > 0:
            fo = open(self.characterizeFile, 'w')
            json.dump(characterize,fo,indent=4)
            fo.close()
        if len(differences) > 0:
            print(f"There are format differences, see {colDifferencesFile}")
            fo = open(self.colDifferencesFile, 'w')
            json.dump(differences,fo,indent=4)
            fo.close()
            quit()
        if self.justCharacterize:
            fo = open(self.colInfoFile, 'w')
            json.dump(self.colInfo,fo,indent=4)
            fo.close()
        return

    def _doCharacterize(self,i,q):
        # get a characterization of question q at index i
        valsD = {}
        valsL = []
        maxVals = 10
        numVals = 0
        for row in self.allLines:
            val = row[i]
            if val not in valsD:
                numVals += 1
                valsD[val] = True
                if numVals <= maxVals:
                    valsL.append(val)
        q['numDistinct'] = numVals
        q['sampleVals'] = valsL

    def _characterize(self):
        differences = []
        characterize = []
        for i in range(len(self.colInfoNew)):
            new = self.colInfoNew[i]
            match = False
            for current in self.colInfo:
                if current['phrase'] == new['phrase']:
                    match = True
                    break
            if match is False:
                new['diffType'] = 'new'
                self._doCharacterize(i,new)
                differences.append(new)
        for i in range(len(self.colInfo)):
            current = self.colInfo[i]
            if self.justCharacterize:
                temp = copy.deepcopy(current)
                self._doCharacterize(i,temp)
                characterize.append(temp)
            match = False
            for new in self.colInfoNew:
                if current['phrase'] == new['phrase']:
                    match = True
                    break
            if match is False:
                current['diffType'] = 'current'
                differences.append(current)
        # also check to see if email appears more than once
        mailIndex = []
        for i in range(len(self.colInfoNew)):
            new = self.colInfoNew[i]
            if new['phrase'].lower().find('mail') >= 0:
                mailIndex.append(i)
        if len(mailIndex) > 1:
            for i in mailIndex:
                new = self.colInfoNew[i]
                new['diffType'] = 'mail'
                differences.append(new)
        return(differences,characterize)

    def getDict(self):
        return self.colInfo

    def getIndex(self,term):
        for i in range(len(self.colInfo)):
            entry = self.colInfo[i]
            if entry['manColName'].find(term) >= 0:
                return i
        return None

    def getPostIndex(self):
        # TODO: this breaks if there is the word "post" in multiple
        # column names for some reason
        if self.postIndex is None:
            self.postIndex = self.getIndex('post')
        return self.postIndex

    def getCountryIndex(self):
        # TODO: same problem, but with country
        if self.countryIndex is None:
            self.countryIndex = self.getIndex('country')
        return self.countryIndex

    def getEmailIndex(self):
        if self.emailIndex is None:
            self.emailIndex = self.getIndex('email')
        return self.emailIndex

    def _getColInfo(self,firstLine,allLines):
        wt = weighTerms()
        # Assign terse column names to each column
        colNames = []
        colInfo = [None] * len(firstLine)
        for i in range(len(firstLine)):
            if i == 0:
                # special case of uid
                colInfo[i] = {'phrase':'uid','autoColName':'uid'}
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
            colInfo[i] = {'phrase':phrase,'autoColName':colName}
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

def addVal(ci,val):
    if ci['type'] == 'boolean':
        if len(val) == 0:
            return "false"
        else:
            return "true"
    if len(val) == 0:
        return "NULL"
    if ci['type'] == 'text':
        if ci['specialHandling'] == 'email':
            return "NULL"
        new = val.replace("'","''")
        if ci['specialHandling'] == 'postIndex':
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

gci = getColInfo(firstLine,allLines,justCharacterize=False)
colInfo = gci.getDict()
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
    sql = str(f"INSERT INTO questions VALUES('{entry['manColName']}', ")
    # need to escape the single quotes in the question phrase
    new = entry['phrase'].replace("'","''")
    sql += str(f"'{new}');\n")
    fo.write(sql)

# And then survey table
geo = postalLatLong()
fo.write('DROP TABLE IF EXISTS survey;\n')
sql = 'CREATE TABLE IF NOT EXISTS survey ('
for entry in colInfo:
    sql += str(f"{entry['manColName']} {entry['type']}, ")
# to the columns given us by col-clear, we want to add a full zip-code,
# longitude and latitude, and a country code
sql += "country_code text, long real, lat real);\n"
fo.write(sql)
for row in allLines:
    sql = "INSERT INTO survey VALUES( "
    for i in range(len(row)):
        ci = colInfo[i]
        if ci['specialHandling'] == 'uid':
            emailIndex = gci.getEmailIndex()
            email = row[emailIndex]
            if len(email) > 0:
                ran = random.randint(1,100000)
                uid = row[i] + str(ran)
            else:
                uid = row[i]
            sql += addVal(colInfo[i],uid) + ", "
        else:
            sql += addVal(colInfo[i],row[i]) + ", "
    # Get country_code, long, and lat using country name and post code
    countryIndex = gci.getCountryIndex()
    if len(row[countryIndex]) == 0:
        cc = None
    else:
        cc = geo.getCC(row[countryIndex])
    if cc is None:
        sql += "NULL, "
    else:
        sql += str(f"'{cc}', ")
    postIndex = gci.getPostIndex()
    post = row[postIndex]
    new = post.upper()
    new = new.replace(' ','')
    (lat,lon) = geo.getLatLong(cc,new)
    if lat is None:
        sql += str(f"NULL, NULL);\n")
    else:
        sql += str(f"{lat}, {lon});\n")
    fo.write(sql)

# And finally symptoms table
fo.write('DROP TABLE IF EXISTS symptoms;\n')
sql = '''CREATE TABLE IF NOT EXISTS symptoms (uid text, symptom text);\n'''
fo.write(sql)
for row in allLines:
    for i in range(len(row)):
        ci = colInfo[i]
        if ci['specialHandling'] == 'symptom' and len(row[i]) > 0:
            sql = f'''INSERT INTO symptoms VALUES('{row[0]}', '{ci['manColName']}');\n'''
            fo.write(sql)


#pp.pprint(colInfo)
fo.close()
