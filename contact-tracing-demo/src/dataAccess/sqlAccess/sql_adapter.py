import datetime
from cache_db import CacheDB
from column_info import ColumnInfo


class SQLAdapter:
    _default_parameters = {
        'anonDB': None,
        'rawDB': None,
    }
    _required_parameters = ['anonDB', 'rawDB']

    def __init__(self, parameters):
        self._parameters = SQLAdapter._default_parameters.copy()
        for parameter, value in parameters.items():
            if parameter in self._required_parameters:
                self._parameters[parameter] = value
        for parameter in self._required_parameters:
            if parameter not in self._parameters:
                raise ValueError(f"Required parameter {parameter} not provided")
        self._anon_db = CacheDB(parameters['anonDB']) if parameters['anonDB'] is not None else None
        self._raw_db = CacheDB(parameters['rawDB']) if parameters['rawDB'] is not None else None

    def load_info_from_cloak(self, table):
        sql = f"SHOW COLUMNS FROM {table};"
        result = self.queryCloak(sql)
        column_info = []
        for row in result:
            name = row[0]
            if row[1] == "integer":
                data_type = int
            elif row[1] == "real":
                data_type = float
            elif row[1] == "text":
                data_type = str
            elif row[1] == "boolean":
                data_type = bool
            elif row[1] == "datetime":
                data_type = datetime.datetime
            elif row[1] == "date":
                data_type = datetime.date
            elif row[1] == "time":
                data_type = datetime.time
            else:
                raise ValueError(f"Returned type {row[1]} is unknown.")
            isolating = row[2]
            column_info.append(ColumnInfo(name, data_type, isolating))
        return column_info

    def load_raw(self, table, columns=None):
        sql = f"SELECT "
        if columns is None:
            sql = sql + f"*"
        else:
            if not columns:
                raise ValueError("Empty columns list provided. Need at least a single column.")
            else:
                first = True
                for column in columns:
                    if first:
                        first = False
                        sql = sql + f" "
                    else:
                        sql = sql + f", "
                    sql = sql + f"{column}"
        sql = sql + f" from {table};"
        return self.queryRaw(sql)

    def queryRaw(self, sql):
        if self._raw_db is None:
            raise ValueError("RawDB not configured")
        return self._raw_db.execute_sql(sql)

    def queryCloak(self, sql):
        if self._anon_db is None:
            raise ValueError("AnonDB not configured")
        return self._anon_db.execute_sql(sql)

    def disconnect(self):
        if self._raw_db is not None and self._raw_db.is_connected():
            self._raw_db.disconnect()
        if self._anon_db is not None and self._anon_db.is_connected():
            self._anon_db.disconnect()
