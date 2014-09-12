import tornado.ioloop
import logging
import logging.handlers

import config
import Gateway


log = logging.getLogger('pymygw')
if not log.handlers:
    formatter = logging.Formatter("%(asctime)s - %(name)s : %(message)s")
    handler = logging.handlers.RotatingFileHandler(config.LogFile, maxBytes=4000000, backupCount=5)
    handler.setFormatter(formatter)
    log.addHandler(handler)
if config.DEBUG:
    log.setLevel(logging.DEBUG)
else:
    log.setLevel(logging.NOTICE)


def checkGateway():
    line = gateway.loop()
    if line is not None:
        log.info('line recieved {0}'.format(line))


def main():
    log.info('starting up')
    serial_loop = tornado.ioloop.PeriodicCallback(checkGateway, 10)
    serial_loop.start()
    log.info('loop started')
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    gateway = Gateway.Gateway()
    main()

