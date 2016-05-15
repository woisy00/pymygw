#!/usr/bin/python
import sys
import signal
import logging
import logging.handlers

import config
from pymygw.Gateway import Gateway
from pymygw.Webinterface import app
from pymygw.MQTT import MQTT
import os

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
    
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    log.addHandler(ch)
if config.DEBUG:
    log.setLevel(logging.DEBUG)
else:
    log.setLevel(logging.INFO)


if not os.path.exists(config.FirmwareDir):
    os.makedirs(config.FirmwareDir)
    
'''
    Publisher
'''
publisher = MQTT()

def exithandler(signal, frame):
    print 'Ctrl-C.... Exiting'
    serialGW.stop()
    publisher.disconnect()
    serialGW.join()
    sys.exit(0)

if __name__ == "__main__":
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, exithandler)
    serialGW = Gateway(publisher)
    serialGW.daemon = True
    serialGW.start()
    app.run(host='0.0.0.0', port=config.WebPort)

