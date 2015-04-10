from threading import Thread
import sys
import signal
import os.path
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


'''
    Publisher
'''
if config.Publisher == 'MQTT':
    from pymygw.MQTT import MQTT
    publisher = MQTT()
elif config.Publisher == 'Openhab':
    from pymygw.OpenHab import Openhab
    #from pymygw import Webinterface
    publisher = Openhab()
else:
    log.error('Unknown Publisher {0}'.format(config.Publisher))
    sys.exit(1)

def exithandler(signal, frame):
    print 'Ctrl-C.... Exiting'
    serialGW.stop()
    thread.join(1)
    sys.exit(0)

if __name__ == "__main__":
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, exithandler)
    serialGW = Gateway(publisher)
    thread = Thread(target=serialGW.loop())
    thread.daemon = True
    thread.start()


