import config
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class MySensorNode(Base):
    __tablename__ = 'sensors'
    id = Column(String, primary_key=True)
    

class MySensor(object):
    def __init__(self):
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
        self._message = m
        self._db = db
        self.__process()


class MySensorMessageType(MySensor):
    '''
        MySensor MessageType Mapping Object
    '''
    def __init__(self):
        self._dict = config.MySensorMessageType
        MySensor.__init__(self)

    def __process(self):
        pass


class MySensorPresentation(MySensor):
    '''
        MySensor Presentation Mapping Object
    '''
    def __init__(self):
        self._dict = config.MySensorPresentation
        MySensor.__init__(self)

    def __process(self):
        pass


class MySensorSetReq(MySensor):
    '''
        MySensor Set and Request Mapping Object
    '''
    def __init__(self):
        self._dict = config.MySensorSetReq
        MySensor.__init__(self)

    def __process(self):
        pass


class MySensorInternal(MySensor):
    '''
        MySensor Internal Mapping Object
    '''
    def __init__(self):
        self._dict = config.MySensorInternal
        MySensor.__init__(self)

    def __process(self):
        if self._message == self.id('I_BATTERY_LEVEL'):
            pass
        elif self._message == self.id('I_TIME'):
            pass
        elif self._message == self.id('I_VERSION'):
            pass
        elif self._message == self.id('I_ID_RESPONSE'):
            pass
        elif self._message == self.id('I_INCLUSION_MODE'):
            pass
        elif self._message == self.id('I_CONFIG'):
            pass
        elif self._message == self.id('I_FIND_PARENT'):
            pass
        elif self._message == self.id('I_FIND_PARENT_RESPONSE'):
            pass
        elif self._message == self.id('I_LOG_MESSAGE'):
            pass
        elif self._message == self.id('I_CHILDREN'):
            pass
        elif self._message == self.id('I_SKETCH_NAME'):
            pass
        elif self._message == self.id('I_SKETCH_VERSION'):
            pass
        elif self._message == self.id('I_REBOOT'):
            pass
        elif self._message == self.id('I_GATEWAY_READY'):
            pass
