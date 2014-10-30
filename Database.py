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

    def initNodes(self):
        self._dbresult = self._cursor.execute('''SELECT id, typ, openhab from sensors''').fetchall()
        if self._dbresult is not None:
            for e in self._dbresult:
                self._node, self._nodetyp, self._nodeopenhab = e
                self._log.debug('Found {0} in DB: typ = {1}, openhab = {2}'.format(self._node,
                                                                                   self._nodetyp,
                                                                                   self._nodeopenhab))
                self.__addtoNodes()

    def __initDB(self):
        self.__connect()
        self._cursor.execute(config.DatabaseTableCreate)
        self._db.commit()
        self.disconnect()

    def __addtoNodes(self):
        self._nodes[self._node] = {'typ': self._nodetyp,
                                   'openhab': self._nodeopenhab}

    def __getNodesfromDB(self):
        try:
            self._dbresult = self._cursor.execute('''SELECT typ, openhab FROM sensors WHERE id=?''', (self._node,)).fetchall()
            self._log.debug('DB Select Result for {0}: {1}'.format(self._node,
                                                                   self._dbresult))
        except:
            self._log.info('Node {0} not found in DB'.format(self._node))
            self._dbresult = None

    def __createNodeID(self, n, s):
        self._node = '{0}_{1}'.format(n, s)

    def freeID(self):
        self._dbresult = self._cursor.execute('''SELECT id FROM sensors ORDER BY id DESC LIMIT 1''').fetchall()
        for e in self._dbresult:
            n, s = e[0].split('_')
            n = int(n) + 1
            return n
        return None

    def check(self, node=None, child=None, typ=None):
        if node is None or child is None or typ is None:
            return None
        self.__createNodeID(node, child)
        self._nodetyp = None
        self._nodeopenhab = None
        if not self._node in self._nodes:
            self.__getNodesfromDB()
            if self._dbresult is not None:
                for e in self._dbresult:
                    self._nodetyp = e[0]
                    if len(e) > 1:
                        self._nodeopenhab = e[1]
                    self.__addtoNodes()
                return self._nodes[self._node]
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
        return None

    def get(self, Node=None):
        self.initNodes()
        if Node is None:
            return self._nodes
        else:
            if Node in self._nodes:
                return self._nodes[Node]

    def add(self, node=None, child=None, typ=None):
        if node is None or child is None or typ is None:
            return None
        self.__createNodeID(node, child)
        self._nodetyp = typ
        self._nodeopenhab = None
        try:
            self._cursor.execute('''INSERT INTO sensors(id, typ, openhab) VALUES (?, ?, ? )''', (self._node,
                                                                                                 self._nodetyp,
                                                                                                 self._nodeopenhab,)).fetchall()
            self._db.commit()
        except Exception, e:
            self._log.error('Exception during INSERT of {0}: {1}'.format(self._node,
                                                                         e))
            return None
        self.__addtoNodes()
        self._log.info('DB Entry added for Node {0}: {1}'.format(self._node,
                                                                 self._nodes[self._node]))
        return True

    def update(self, node=None, openhab=None):
        if node is None:
            return None
        if self.get(Node=node) is None:
            self._log.error('Node {0} unknown, can not glue to {1}'.format(node,
                                                                           openhab))
            return None
        try:
            self._cursor.execute('''UPDATE sensors SET openhab=? WHERE id=?''', (openhab, node))
            self._db.commit()
        except Exception, e:
            self._log.error('Exception during UPDATE of {0}: {1}'.format(node,
                                                                         e))
            return None
        self.initNodes()
        self._log.info('Updated Sensor {0} to Openhab {1}'.format(node, openhab))
        return self.get(Node=node)

