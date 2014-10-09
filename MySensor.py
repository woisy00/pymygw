from time import time

import config
import logging


class MySensor():
    def __init__(self):
        self._log = logging.getLogger('pymygw')
        '''
            RevertDict id -> Name
        '''
        self.RevertDict = {}
        for k, v in self._dict.iteritems():
            self.RevertDict[v['id']] = k

    def __prepare(self, i, t='str'):
        if t == 'str' and isinstance(i, str):
            #force upper case
            self._request = i.upper()
        elif t == 'int':
            self._request = self.__toInt(i)

    def __searchRequest(self):
        self._answer = None
        if self._request in self._dict:
            self._answer = self._dict[self._request][self._lf]

    def __toInt(self, i):
        return int(float(i))

    def process(self):
        # replaced by child process
        raise NotImplementedError()

    def name(self, i):
        self.__prepare(i, t='int')
        if self._request in self.RevertDict:
            return self.RevertDict[self._request]

    def id(self, i):
        self.__prepare(i)
        self._lf = 'id'
        self.__searchRequest()
        return self._answer

    def comment(self, i):
        self.__prepare(i)
        self._lf = 'comment'
        self.__searchRequest()
        return self._answer

    def message(self, m, db):
        self._cmd = None
        self._message = m
        self._db = db
        self.process()
        if self._cmd is not None:
            self._log.debug('Created CMD: {0}'.format(self._cmd))
        return self._cmd


class MySensorMessageType(MySensor):
    '''
        MySensor MessageType Mapping Object
    '''
    def __init__(self):
        self._dict = config.MySensorMessageType
        MySensor.__init__(self)

    def process(self):
        '''TODO'''
        return self._cmd


class MySensorPresentation(MySensor):
    '''
        MySensor Presentation Mapping Object
    '''
    def __init__(self):
        self._dict = config.MySensorPresentation
        MySensor.__init__(self)

    def process(self):
        '''TODO'''
        pass


class MySensorSetReq(MySensor):
    '''
        MySensor Set and Request Mapping Object
    '''
    def __init__(self, openhab):
        self._dict = config.MySensorSetReq
        MySensor.__init__(self)
        self._openhab = openhab

    def process(self):
        self._log.debug('Processing Set/Req Message')
        if self._message['messagetype'] == 'SET':
            self.__set()

    def __set(self):
        self._log.debug('Message in set: {0}'.format(self._message))
        c = self._db.check(node=self._message['nodeid'],
                           child=self._message['childid'],
                           typ=self.name(self._message['subtype']))

        #add new node/child to db
        if c is None:
            self._log.debug('Trying to add {0} to DB'.format(self._message))
            a = self._db.add(node=self._message['nodeid'],
                             child=self._message['childid'],
                             typ=self.name(self._message['subtype']))
            if a is None:
                self._log.error('Add Node Failed: {0}'.format(self._message))
        #push new value to openhab
        elif c['openhab'] is not None:
            self._log.debug('Try to push value to openhab: {0}'.format(self._message))
            self._openhab.Set(c['openhab'], value=self._message['payload'])


class MySensorInternal(MySensor):
    '''
        MySensor Internal Mapping Object
    '''
    def __init__(self):
        self._dict = config.MySensorInternal
        MySensor.__init__(self)

    def process(self):
        self._log.debug('Processing Internal Message')
        self._messagetype = config.MySensorMessageType['INTERNAL']['id']

        if self._message['subtype'] == self.id('I_BATTERY_LEVEL'):
            pass
        elif self._message['subtype'] == self.id('I_TIME'):
            self._log.debug('Processed by I_TIME: {0}'.format(self._message))
            self.__GetTime()
        elif self._message['subtype'] == self.id('I_VERSION'):
            pass
        elif self._message['subtype'] == self.id('I_ID_REQUEST'):
            self._log.debug('Processed by I_ID_REQUEST: {0}'.format(self._message))
            self.__IDRequest()
        elif self._message['subtype'] == self.id('I_ID_RESPONSE'):
            pass
        elif self._message['subtype'] == self.id('I_INCLUSION_MODE'):
            pass
        elif self._message['subtype'] == self.id('I_CONFIG'):
            self._log.debug('Processed by I_CONFIG: {0}'.format(self._message))
            self.__Config()
        elif self._message['subtype'] == self.id('I_FIND_PARENT'):
            pass
        elif self._message['subtype'] == self.id('I_FIND_PARENT_RESPONSE'):
            pass
        elif self._message['subtype'] == self.id('I_LOG_MESSAGE'):
            pass
        elif self._message['subtype'] == self.id('I_CHILDREN'):
            pass
        elif self._message['subtype'] == self.id('I_SKETCH_NAME'):
            pass
        elif self._message['subtype'] == self.id('I_SKETCH_VERSION'):
            pass
        elif self._message['subtype'] == self.id('I_REBOOT'):
            pass
        elif self._message['subtype'] == self.id('I_GATEWAY_READY'):
            pass

    def __IDRequest(self):
        '''
            create new id for unknown nodes
            and send it as ID_RESPONSE
        '''
        newID = self._db.freeID()
        if newID is not None:
            self._cmd = {'nodeid': 255,
                         'childid': 255,
                         'messagetype': self._messagetype,
                         'subtype': self.id('I_ID_RESPONSE'),
                         'payload': newID}

    def __Config(self):
        '''
            return config
            only used for get_metric afaik
        '''
        self._cmd = {'nodeid': self._message['nodeid'],
                     'childid': 255,
                     'messagetype': self._messagetype,
                     'subtype': self.id('I_CONFIG'),
                     'payload': config.UnitSystem}

    def __GetTime(self):
        self._cmd = {'nodeid': self._message['nodeid'],
                     'childid': self._message['childid'],
                     'messagetype': self._messagetype,
                     'subtype': self.id('I_TIME'),
                     'payload': int(time())}


