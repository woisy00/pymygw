from tornado.ioloop import IOLoop
from threading import Thread, Event
from sys import exit
import time
import os
import logging
import logging.handlers

import config
from pymygw.Gateway import Gateway


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


if config.Publisher == 'MQTT':
    from pymygw.MQTT import MQTT
    publisher = MQTT()
elif config.Publisher == 'Openhab':
    from tornado.web import Application, StaticFileHandler
    from pymygw.OpenHab import Openhab
    from pymygw import Webinterface
    publisher = Openhab()

    TornadoLoop = None
    Web = Application([
        (r'/do', Webinterface.CommandHandler, dict(openhab=publisher)),
        (r'/static/(.*)', StaticFileHandler, {'path': os.path.join(config.WebDir, 'static')}),
        (r'/', Webinterface.IndexHandler, dict(openhab=publisher)),
    ])

    Web.listen(config.WebPort)

    logging.getLogger("tornado.access").addHandler(handler)
    logging.getLogger("tornado.access").propagate = False
    logging.getLogger("tornado.application").addHandler(handler)
    logging.getLogger("tornado.application").propagate = False
    logging.getLogger("tornado.general").addHandler(handler)
    logging.getLogger("tornado.general").propagate = False


else:
    log.error('Unknown Publisher {0}'.format(config.Publisher))
    exit(1)


if __name__ == "__main__":
    serialGW = Gateway(publisher)
    thread = Thread(target=serialGW.loop())
    thread.daemon = True
    try:
        thread.start()
    except KeyboardInterrupt, SystemExit:
        print 'stopping'
        try:
            publisher.disconnect()
            serialGW._run.clear()
        except Exception, e:
            print e


