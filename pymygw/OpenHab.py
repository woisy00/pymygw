import requests
from datetime import datetime
from logging import getLogger

import config
import Database
import tools

class Openhab(object):
    def __init__(self):
        self._log = getLogger('pymygw')
        self._rest = config.OpenhabAPI
        self._db = Database.Database()
        self._items = {}

    def Items(self):
        if not self._items:
            self.__getItems()
        else:
            delta = datetime.now() - self._items['cache']
            if delta.seconds > config.OpenhabCacheTimeout:
                self._log.info('Openhab Items Cache expired, reloading Items')
                self.__getItems()
        return self._items

    def publish(self, msg):
        self._ok = False
        self._log.debug('Try to push value to openhab: {0}'.format(msg))
        self._data = tools.checkKeys(msg, ('payload', 'nodeid', 'childid'))
        if self._data:
            self._data['openhab'] = self._db.openhab(node=self._data['nodeid'],
                                                     sensor=self._data['childid'])
            if self._data['openhab'] and self._data['openhab'] in self.Items():
                otype = self.Items()[self._data['openhab']]
                if otype == 'ContactItem':
                    if self._data['payload'] == '0':
                        self._payload = 'CLOSED'
                    elif self._data['payload'] == '1':
                        self._payload = 'OPEN'
                else:
                    self._payload = self._data['payload']
                if self._payload is not None:
                    self._url = '{0}/{1}/state'.format(config.OpenhabAPI,
                                                       self._data['openhab'])
                    self._log.debug('Openhab put url {0} with data {1}'.format(self._url,\
                                                                               self._payload))
                    self.__requestPut()
                    if self._ok:
                        self._log.info('Openhab updated successfully:\n\
                                        Node: {nodeid},\n\
                                        Sensor: {childid}\n\
                                        Openhab: {openhab}\n\
                                        Value: {payload}'.format(**self._data))

                    else:
                        self._log.error('Openhab update failed:\n\
                                         Node: {nodeid},\n\
                                         Sensor: {childid}\n\
                                         Openhab: {openhab}\n\
                                         Value: {payload}'.format(**self._data))

                else:
                    self._log.error('Openhab cant parse value: {0} for item: {1}'.format(self._data['payload'],\
                                                                                         self._data['openhab']))

            else:
                self._log.error('Openhab entry missing: {0}'.format(self._data))

    def __requestPut(self):
        h = {'Content-Type': 'text/plain',
             'Accept': 'application/json'}
        try:

            r = requests.put(url=self._url,
                             data=self._payload,
                             headers=h,
                             timeout=5)
        except Exception, e:
            self._log.error('Exception on Openhab Put: {0}'.format(e))
            return
        self.__requestCheckandParse(r)

    def __requestGet(self):
        self._response = None
        h = {'Accept': 'application/json'}
        try:
            r = requests.get(url=self._url,
                             headers=h,
                             timeout=5)
        except Exception, e:
            self._log.error('Exception on Openhab Put: {0}'.format(e))
            return
        self.__requestCheckandParse(r)

    def __requestCheckandParse(self, r):
        if r.status_code == requests.codes.ok:
            self._ok = True
            if len(r.content) > 0:
                try:
                    self._response = r.json()
                except Exception, e:
                    self._log.error('Openhab json load failed error: {0}'
                                    'with content: {1}'.format(e, r.content))
                    self._ok = False
        else:
            self._log.error('Openhab got error {0}'
                            'with HTTP Code: {1}'.format(r.content, r.status_code))

    def __getItems(self):
        self._url = '{0}/?type=json'.format(self._rest)
        self.__requestGet()
        if self._response is not None:
            self._items['cache'] = datetime.now()
            for e in self._response[config.OpenhabAPIList]:
                self._items[e['name']] = e['type']
            self._log.debug('Openhab Items: {0}'.format(self._items))
