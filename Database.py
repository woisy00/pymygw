'''

    TODO
          - add new function new_id to generate new ids for new nodes
          - simplify it
          -
'''

import sqlite3
import logging

import config


class Database(object):
    def __init__(self):
        self._log = logging.getLogger('pymygw')
        self._db = None
        self._cursor = None
        self._isConnected = False
        self._nodes = {}
        self.__initDB()
        self.__initNodes()

    def disconnect(self):
        if self._isConnected:
            self._db.commit()
            self._db.close()

    def __connect(self):
        try:
            self._db = sqlite3.connect(config.Database)
            self._cursor = self._db.cursor()
        except Exception, e:
            self._log.error('DB connect failed: {0}'.format(e))

    def __initNodes(self):
        self.__executeDB('''SELECT id, typ, openhab from sensors''')
        if self._dbresult is not None:
            for e in self._dbresult:
                self._node, self._nodetyp, self._nodeopenhab = e
                self._log.debug('Found {0} in DB: typ = {1}, openhab = {2}'.format(self._node,
                                                                                   self._nodetyp,
                                                                                   self._nodeopenhab))
                self.__addtoNodes()
        self.__closeCursor(c)

    def __initDB(self):
        self.__executeDB(config.DatabaseTableCreate)

    def __executeDB(self, c):
        self._dbresult = self.cursor.execute(c).fetchall()
        self._db.commit()

    def __addtoNodes(self):
        self._nodes[self._node] = {'typ': self._nodetyp,
                                   'openhab': self._nodeopenhab}

    def __getNodesfromDB(self):
        try:
            self.__executeDB('''SELECT typ, proto, sketchname, sketchversion, obenhab FROM sensors WHERE id=?''', (self._node,))
            self._log.debug('DB Select Result for {0}: {1}'.format(self._node,
                                                                   self._dbresult))
        except:
            self._log.info('Node {0} not found in DB'.format(self._node))
            self._dbresult = None
            self._nodetyp = typ

    def __createNodeID(self, n, s):
        self._node = '{0}_{1}'.format(n, s)

    def __freeID(self):
        self.__executeDB('''SELECT id FROM sensors ORDER BY id DESC LIMIT 1''')
        if self._dbresult is not None:
            for e in self._dbresult:
                n, s = e[0].split('_')
                n = int(n) + 1
                return n
        return None

    def check(self, node=None, sensor=None, typ=None):
        if node is None or sensor is None or typ is None:
            return None
        self.__createNodeID()
        self.__getNodesfromDB()
        self._nodetyp = None
        self._nodeopenhab = None
        if not self._node in self._nodes:
            if self._dbresult is not None:
                for e in self._dbresult:
                    self._nodetyp = e[0]
                    if len(e) > 1:
                        self._nodeopenhab = e[1]
                    self.__addtoNodes()
            else:
                self.add(
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

    def get(self, Node=None):
        if Node is None:
            return self._nodes
        else:
            if Node in self._nodes:
                return self._nodes[Node]

    def add(self, protoVersion=None, sketchname=None, sketchversion=None):
        nodeid = self.__freeID():
        self.__executeDB('''INSERT INTO sensors(id, typ, openhab) VALUES (?, ?, ? )''', (self._node,
                                                                                         self._nodetyp,
                                                                                         self._nodeopenhab))
        self.__addtoNodes()
        self._log.info('DB Entry added for Node {0}: {1}'.format(self._node,
                                                                 self._nodes[self._node]))

