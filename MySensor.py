import config


class MySensor(object):
    def __init__(self):
        self.RevertDict = {}
        for k, v in self._dict.iteritems():
            self.RevertDict[v['id']] = k

    def __prepare(self, i):
        self._request = i
        if isinstance(i, int) and i in self.RevertDict:
            self.__request = self.RevertDict[i]
        elif isinstance(i, str):
            #force upper case
            self.__request = i.upper()

    def __searchRequest(self):
        self._answer = None
        if self._request in self._dict:
            self._answer = self._dict[self._request][self._lf]

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
    def __init__(self):
        self._dict = config.MySensorMessageType
        MySensor.__init__(self)


class MySensorPresentation(MySensor):
    def __init__(self):
        self._dict = config.MySensorPresentation
        MySensor.__init__(self)


class MySensorSetReq(MySensor):
    def __init__(self):
        self._dict = config.MySensorSetReq
        MySensor.__init__(self)


class MySensorInternal(MySensor):
    def __init__(self):
        self._dict = config.MySensorInternal
        MySensor.__init__(self)
