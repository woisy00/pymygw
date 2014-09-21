from tornado.web import RequestHandler
import logging
import json


class Nodes(RequestHandler):
    def initialize(self, database, openhab):
        self._db = database
        self._openhab = openhab

    def get(self):
        r = self._db.get()
        h = self._openhab.Items()
        response = json.dumps({'nodes': r,
                               'openhab': h})
        self.write(response)


class Node(RequestHandler):
    def initialize(self, database, openhab):
        self._log = logging.getLogger('pymygw')
        self._db = database
        self._openhab = openhab

    def get(self, n):
        r = self._db.get(Node=n)
        response = json.dumps({n: r})
        self.write(response)

    def put(self, n):
        d = json.loads(self.request.body)
        try:
            o = d['openhab']
        except:
            response = json.dumps({n, 'ERROR'})
            self.write(response)
        if o is not None:
            self._log.info('API Put call to glue {0}:{1}'.format(n, o))
            if o in self._openhab.Items():
                r = self._db.glue(node=n, openhab=o)
            response = json.dumps({n: r})
            try:
                self.write(response)
                self.finish()
            except:
                self.connection_closed = True

    def on_finish(self):
        pass
