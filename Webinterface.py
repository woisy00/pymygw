from jinja2 import Environment, FileSystemLoader
from tornado.web import RequestHandler, HTTPError
import os
import logging
import json

import config

templateFile = "index.html"
templateLoader = FileSystemLoader(searchpath=os.path.join(config.WebDir, 'templates'))
templateEnv = Environment(loader=templateLoader)
template = templateEnv.get_template(templateFile)


class IndexHandler(RequestHandler):
    def initialize(self, database, openhab):
        self._logging = logging.getLogger('pymygw')
        self._database = database
        self._openhab = openhab
        self._output = template.render(items=self._database.get(),
                                       openhab=self.__prepareOpenhabItems())

    def get(self):
        self.write(self._output)

    def __prepareOpenhabItems(self):
        l = []
        for e, v in self._openhab.Items().iteritems():
            if str(v) in ('NumberItem'):
                l.append(e)
        return l


class CommandHandler(RequestHandler):
    def initialize(self, database, openhab):
        self._logging = logging.getLogger('pymygw')
        self._database = database
        self._openhab = openhab

    def post(self):
        try:
            data = json.loads(self.request.body)
            self._action = data['action']
            self._sensor = data['sensor']
            self._ohitem = data['openhab']
        except:
            raise HTTPError(400, 'Bad Request {0}'.format(data))

        self.__checkSensor()
        self.__checkOpenhab()

        self._logging.info('Webinterface Action {0}, Sensor {1}, Openhab {2}'.format(self._action, self._sensor, self._ohitem))
        if self._action == 'update':
            self._logging.info('Would update {0}'.format((self._action, self._sensor, self._ohitem)))
            self.__update()
        elif self._action == 'delete':
            self._logging.info('Would delete {0}'.format((self._action, self._sensor, self._ohitem)))
            self.__delete()
        else:
            raise HTTPError(400, 'Action unknown {0}'.format(self._action))

    def __checkSensor(self):
        if self._database.get(Node=self._sensor) is None:
            raise HTTPError(400, 'Sensor unknown {0}'.format(self._sensor))

    def __checkOpenhab(self):
        if not self._ohitem in self._openhab.Items():
            raise HTTPError(400, 'Openhab Item unknown {0}'.format(self._ohitem))

    def __delete(self):
        r = self._database.update(node=self._sensor)
        if r is None:
            raise HTTPError(400, 'Delete failed {0}'.format(self._sensor))
        self.set_status(200, reason='OK')

    def __update(self):
        r = self._database.update(node=self._sensor, openhab=self._ohitem)
        if r is None:
            raise HTTPError(400, 'Update failed {0}, {1}'.format(self._sensor, self._ohitem))
        self.set_status(200, reason='OK')
