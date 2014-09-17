from threading import Thread
import sys
import signal
import logging
import logging.handlers

import config
import Gateway
import Database


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

log.debug('Try to open DB connection')
db = Database.Database()

THREADS = []


class GatewayThread(Thread):
    def __init__(self):
        self.alive = True
        self.gateway = Gateway.Gateway(db)
        Thread.__init__(self)

    def run(self):
        while self.alive:
            self.gateway.loop()
        self.gateway.stop()


def stop(signal, frame):
    log.info('CTRL-C recieved, stopping')
    for t in THREADS:
        t.alive = False
    sys.exit(0)


def main():
    global THREADS
    log.info('starting up')
    thread = GatewayThread()
    thread.start()
    log.info('loop started')
    THREADS.append(thread)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, stop)
    main()
    while True:
        signal.pause()
