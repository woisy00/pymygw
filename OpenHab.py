import json
import urllib2
import logging

import config


class Openhab(object):
    def __init__(self, db):
        self._log = logging.getLogger('pymygw')
        self._rest = '{0}?type=json'.format(config.OpenhabAPI)
        self._db = db
        self._items = {}

        self.__getItems()

    def Items(self):
        return self._items

    def __getItems(self):
        try:
            self._response = json.load(urllib2.urlopen(self._rest))
            for e in self._response[config.OpenhabAPIList]:
                self._items[e['name']] = e['type']
            self._log.debug('Openhab Items: {0}'.format(self._items))
        except Exception, e:
            self._log.error('cant connect to Openhab Rest {0}: {1}'.format(self._rest,
                                                                           e))
            return
