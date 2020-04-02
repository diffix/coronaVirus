import json

class colsQuestions:
    ''' generates a csv file of column_name,question
## makeQuestionsCsv.py

Produces `colsAndQuestions.csv`, which contains the column names and
associated questions, sorted alphabetically by column name.

### To run

Can be run standalone (`python makeQuestionsCsv.py`)
Is called by makeSqlFromCsv.py
    '''

    def __init__(self,colInfo,outFile='colsAndQuestions.csv'):
        '''
        outFile: full csv file name
        colInfo: python structure taken from colInfo.json
        '''
        csvOut = []
        for item in colInfo:
            line = str(f'''{item['manColName']},"{item['phrase']}"\n''')
            csvOut.append(line)
        csvOut.sort()
        fo = open(outFile,'w')
        fo.write("Column name,Question\n")
        for line in csvOut:
            fo.write(line)
        fo.close()
        return

if __name__ == "__main__":
    fi = open('colInfo.json','r')
    colInfo = json.load(fi)
    fi.close()
    colsQuestions(colInfo)
