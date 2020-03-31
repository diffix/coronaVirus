import json
import sqlite3
import os.path
import pprint


'''
geonames-postal-code.json is a list of data fields like this:
{   'datasetid': 'geonames-postal-code@public-us',
    'fields': {   'accuracy': '4',
                  'admin_code1': 'Z',
                  'admin_name1': 'Santa Cruz',
                  'coordinates': [-46.4333, -67.5333],
                  'country_code': 'AR',
                  'latitude': '-46.4333',
                  'longitude': '-67.5333',
                  'place_name': 'CALETA OLIVIA',
                  'postal_code': '9011'},
    'geometry': {'coordinates': [-67.5333, -46.4333], 'type': 'Point'},
    'record_timestamp': '2020-03-18T16:08:45.005+01:00',
    'recordid': '7280fc1c19f80d069cc58aa6216c5567cc5d9cd3'}
also 'admin_codes and admin_names 2 and 3
also accuracy somewhere
'''

class postalLatLong:
    _dbName = 'geonames.db'
    _data = None
    _ccCodes = None
    _dataFile = 'geonames-postal-code.json'
    _ccFile = 'countryCodes.json'
    _conn = None
    _cur = None
    pp = None

    def __init__(self,flush=False):
        self.pp = pprint.PrettyPrinter(indent=4)
        if flush is False and os.path.isfile(self._dbName):
            # We have already built the database
            self._conn = sqlite3.connect(self._dbName)
            self._cur = self._conn.cursor()
        else:
            self._buildDatabase()

    def _buildDatabase(self):
        if os.path.isfile(self._dataFile):
            with open(self._dataFile, 'r') as fi:
                self._data = json.load(fi)
        else:
            print(f"Can't find file {self.dataFile}")
            quit()
        if os.path.isfile(self._ccFile):
            with open(self._ccFile, 'r') as fi:
                self._ccCodes = json.load(fi)
        else:
            print(f"Can't find file {self.ccFile}")
            quit()
        # Index the country codes by country code
        ccIndex = {}
        for cc in self._ccCodes:
            ccIndex[cc['Code']] = cc['Name']
        self._conn = sqlite3.connect(self._dbName)
        self._cur = self._conn.cursor()
        self._cur.execute("DROP TABLE IF EXISTS zip_lat_long")
        self._cur.execute('''CREATE TABLE IF NOT EXISTS zip_lat_long 
             (admin_code text,
             accuracy integer,
             admin_name text, 
             cc text,
             country text,
             lat real,
             long real,
             post text)
             ''')
        for record in self._data:
            datum = self._getDatumFromRecord(record)
            self._addCountryToDatum(datum,ccIndex)
            sql = self._makeInsertSql(datum)
            self._cur.execute(sql)
        self._conn.commit()

    def _makeInsertSql(self,datum):
        sql = 'INSERT INTO zip_lat_long VALUES('
        if 'admin_code' in datum:
            sql += str(f"'{datum['admin_code']}', ")
        else:
            sql += 'NULL, '
        if 'accuracy' in datum:
            sql += str(f"'{datum['accuracy']}', ")
        else:
            sql += 'NULL, '
        if 'admin_name' in datum:
            name = datum['admin_name'].replace("'","''")
            sql += str(f"'{name}', ")
        else:
            sql += 'NULL, '
        sql += str(f"'{datum['cc']}', ")
        country = datum['country'].replace("'","''")
        sql += str(f"'{country}', ")
        sql += str(f"{datum['lat']}, ")
        sql += str(f"{datum['long']}, ")
        sql += str(f"'{datum['post']}')")
        return sql

    def _addCountryToDatum(self,datum,ccIndex):
        if datum['cc'] not in ccIndex:
            print(f"CC {datum['cc']} not in ccIndex!")
            quit()
        datum['country'] = ccIndex[datum['cc']]

    def _getDatumFromRecord(self,record):
        datum = {}
        if 'fields' not in record:
            self._doFail("fields not in record",record)
        fd = record['fields']
        for thing in ['country_code','latitude',
                'longitude','postal_code']:
            if thing not in fd:
                msg = str(f"{thing} not in fields")
                self._doFail(msg,record)
        datum['lat'] = fd['latitude']
        datum['long'] = fd['longitude']
        datum['cc'] = fd['country_code']
        datum['post'] = fd['postal_code']
        if 'admin_code1' in fd:
            datum['admin_code'] = fd['admin_code1']
        if 'admin_name1' in fd:
            datum['admin_name'] = fd['admin_name1']
        if 'accuracy' in fd:
            datum['accuracy'] = fd['accuracy']
        return datum

    def _doFail(self,msg,record):
        print(msg)
        self.pp.pprint(record)
        quit()

if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=4)
    x = postalLatLong(flush=False)
