import sqlite3

import config


class Database(object):
    def __init__(self):
        self._db = None
        self._cursor = None
        self._isConnected = False
        self.__connect()

    def __connect(self):
        try:
            self._db = sqlite3.connect(config.Database)
            self._cursor = self._db.cursor()
            self._cursor.execute(config.DatabaseTableCreate)
            self._db.commit()
            self._isConnected = True
        except Exception, e:
            print e
            #self._log.error('DB connect failed: {0}'.format(e))
            self._isConnected = False

    def __disconnect(self):
        if self._isConnected:
            self._db.commit()
            self._db.close()

    def cursor(self):
        return self._cursor

    def commit(self):
        self._db.commit()
