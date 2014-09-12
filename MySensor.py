import config


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


class MySensorMessageType(MySensor):
    '''
        MySensor MessageType Mapping Object
    '''
    def __init__(self):
        self._dict = config.MySensorMessageType
        MySensor.__init__(self)


class MySensorPresentation(MySensor):
    '''
        MySensor Presentation Mapping Object
    '''
    def __init__(self):
        self._dict = config.MySensorPresentation
        MySensor.__init__(self)


class MySensorSetReq(MySensor):
    '''
        MySensor Set and Request Mapping Object
    '''
    def __init__(self):
        self._dict = config.MySensorSetReq
        MySensor.__init__(self)


class MySensorInternal(MySensor):
    '''
        MySensor Internal Mapping Object
    '''
    def __init__(self):
        self._dict = config.MySensorInternal
        MySensor.__init__(self)
