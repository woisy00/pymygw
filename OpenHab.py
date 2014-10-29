import logging
import requests
from datetime import datetime

import config


class Openhab(object):
    def __init__(self):
        self._log = logging.getLogger('pymygw')
        self._rest = config.OpenhabAPI
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

    def Set(self, item=None, value=None):
        self._ok = False
        if item is None or value is None:
            self._log.error('Openhab missing item or value: item={0}, value={0}'.format(item, value))
            return
        elif item not in self.Items():
            self._log.error('Openhab unknown item: {0}'.format(item))
            return

        otype = self.Items()[item]
        self._data = None
        if otype == 'ContactItem':
            if value == '0':
                self._data = 'CLOSED'
            elif value == '1':
                self._data = 'OPEN'
        else:
            self._data = value
        if self._data is not None:
            self._url = '{0}/{1}/state'.format(config.OpenhabAPI, item)
            self._log.debug('Openhab put url {0} with data {1}'.format(self._url, self._data))
            self.__requestPut()
        else:
            self._log.error('Openhab cant parse value: {0} for item: {1}'.format(value, item))
        return self._ok

    def __requestPut(self):
        h = {'Content-Type': 'text/plain',
             'Accept': 'application/json'}
        try:

            r = requests.put(url=self._url,
                             data=self._data,
                             headers=h,
                             timeout=5)
        except Exception, e:
            self._log.error('Exception on Openhab Put: {0}'.format(e))
            return False
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
            return False
        self.__requestCheckandParse(r)

    def __requestCheckandParse(self, r):
        if r.status_code == requests.codes.ok:
            self._ok = True
            if len(r.content) > 0:
                try:
                    self._response = r.json()
                except Exception, e:
                    self._log.error('Openhab json load failed error: {0} with content: {1}'.format(e, r.content))
                    self._ok = False
        else:
            self._log.error('Openhab get error {0} with HTTP Code: {1}'.format(r.content, r.status_code))

    def __getItems(self):
        self._url = '{0}/?type=json'.format(self._rest)
        self.__requestGet()
        if self._response is not None:
            self._items['cache'] = datetime.now()
            for e in self._response[config.OpenhabAPIList]:
                self._items[e['name']] = e['type']
            self._log.debug('Openhab Items: {0}'.format(self._items))
