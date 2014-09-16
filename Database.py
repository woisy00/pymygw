import sqlite3
import config

import logging


class Database(object):
    def __init__(self):
        self._log = logging.getLogger('pymygw')
        self._db = None
        self._cursor = None
        self._isConnected = False
        self.__connect()
        self._nodes = {}

    def __connect(self):
        try:
            self._db = sqlite3.connect(config.Database)
            self._cursor = self._db.cursor()
            self._cursor.execute(config.DatabaseTableCreate)
            self._db.commit()
            self._isConnected = True
        except Exception, e:
            print e
            self._log.error('DB connect failed: {0}'.format(e))
            self._isConnected = False

    def __disconnect(self):
        if self._isConnected:
            self._db.commit()
            self._db.close()

    def __commit(self):
        self._db.commit()

    def __addtoNodes(self):
        self._nodes[self._node] = {'typ': self._nodetyp,
                                   'openhab': self._nodeopenhab}

    def check(self, node=None, sensor=None, typ=None):
        if node is None or sensor is None or typ is None:
            return None

        self._node = '{0}_{1}'.format(node, sensor)
        self._nodetyp = None
        self._nodeopenhab = None
        if not self._node in self._nodes:
            try:
                self._dbresult = self._cursor.execute('''SELECT typ, obenhab FROM sensors WHERE id=?''', (self._node,)).fetchall()
                self._log.debug('DB Select Result for {0}: {1}'.format(self._node,
                                                                       self._dbresult))
            except:
                self._log.info('Node {0} not found in DB'.format(self._node))
                self._dbresult = None
                self._nodetyp = typ

            if self._dbresult is not None:
                for e in self._dbresult:
                    self._nodetyp = e[0]
                    if len(e) > 1:
                        self._nodeopenhab = e[1]
                    self.__addtoNodes()
            else:
                self._cursor.execute('''INSERT INTO sensors(id, typ, openhab) VALUES (?, ?, ? )''', (self._node,
                                                                                                     self._nodetyp,
                                                                                                     self._nodeopenhab))
                self.__commit()
                self.__addtoNodes()
                self._log.info('DB Entry added for Node {0}: {1}'.format(self._node,
                                                                         self._nodes[self._node]))
        else:
            self._log.debug('Node {0} found in nodes: {1}'.format(self._node,
                                                                  self._nodes[self._node]))
            self._nodetyp = self._nodes[self._node]['typ']
            self._nodeopenhab = self._nodes[self._node]['openhab']
            if typ != self._nodetyp:
                self._log.error('DB Sensor Typ {1} for {0} does not match reported Typ {2}'.format(self._node,
                                                                                                   self._nodetyp,
                                                                                                   typ))
                return None

        return self._nodes[self._node]
