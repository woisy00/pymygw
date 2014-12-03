from tornado.ioloop import IOLoop
from tornado.web import Application, StaticFileHandler
from threading import Thread
from sys import exit
import os
import signal
import logging
import logging.handlers

import config
import Gateway
import OpenHab
import MQTT


'''
    Logging
'''
log = logging.getLogger('pymygw')
log.propagate = False
if not log.handlers:
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler = logging.handlers.RotatingFileHandler(config.LogFile, maxBytes=4000000, backupCount=5)
    handler.setFormatter(formatter)
    log.addHandler(handler)
if config.DEBUG:
    log.setLevel(logging.DEBUG)
else:
    log.setLevel(logging.INFO)


#db = Database.Database()
if config.Publisher == 'MQTT':
    publisher = MQTT.MQTT()
elif config.Publisher == 'Openhab':
    publisher = OpenHab.Openhab()

    '''
        we only need the webinterface if we use the openhab rest api
    '''
    import Webinterface
    TornadoLoop = None
    Web = Application([
        (r'/do', Webinterface.CommandHandler, dict(openhab=publisher)),
        (r'/static/(.*)', StaticFileHandler, {'path': os.path.join(config.WebDir, 'static')}),
        (r'/', Webinterface.IndexHandler, dict(openhab=publisher)),
    ])
    logging.getLogger("tornado.access").addHandler(handler)
    logging.getLogger("tornado.access").propagate = False
    logging.getLogger("tornado.application").addHandler(handler)
    logging.getLogger("tornado.application").propagate = False
    logging.getLogger("tornado.general").addHandler(handler)
    logging.getLogger("tornado.general").propagate = False


else:
    log.error('Unknown Publisher {0}'.format(config.Publisher))
    exit(1)

#openhab = OpenHab.Openhab()
#mqtt = MQTT.MQTT()


class SerialThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.gw = Gateway.Gateway(publisher)

    def run(self):
        while True:
            self.gw.loop()


def stop(signal, frame):
    global TornadoLoop
    log.info('CTRL-C recieved, stopping')
    try:
        publisher.disconnect()
    except:
        pass
    TornadoLoop.stop()


def main():
    global TornadoLoop
    serialGW = SerialThread()
    serialGW.daemon = True
    serialGW.start()
    if config.Publisher == 'Openhab':
        Web.listen(config.WebPort)
    TornadoLoop = IOLoop.instance()
    TornadoLoop.start()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, stop)
    main()
