from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.web import Application
import signal
import logging
import logging.handlers

import config
import Gateway
import Database
import Api


'''
    Logging
'''
log = logging.getLogger('pymygw')
if not log.handlers:
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler = logging.handlers.RotatingFileHandler(config.LogFile, maxBytes=4000000, backupCount=5)
    handler.setFormatter(formatter)
    log.addHandler(handler)
if config.DEBUG:
    log.setLevel(logging.DEBUG)
else:
    log.setLevel(logging.NOTICE)

db = Database.Database()
TornadoLoop = None
SerialLoop = None
RestApi = Application([
    (r'/api/nodes/([0-9]+_[0-9]+)', Api.Node),
    (r'/api/nodes', Api.Nodes),
])


def startgw():
    gw.loop()


def stop(signal, frame):
    global TornadoLoop
    global SerialLoop
    log.info('CTRL-C recieved, stopping')
    SerialLoop.stop()
    TornadoLoop.stop()


def main():
    global TornadoLoop
    global SerialLoop
    log.info('starting up')
    SerialLoop = PeriodicCallback(startgw, 10)
    SerialLoop.start()
    RestApi.listen(5000)
    TornadoLoop = IOLoop.instance()
    TornadoLoop.start()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, stop)
    gw = Gateway.Gateway(db)
    main()
