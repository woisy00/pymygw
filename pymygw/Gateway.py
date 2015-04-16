import serial
from time import sleep
from logging import getLogger

import config
import MySensor


class Gateway(object):
    def __init__(self, publisher):
        self._log = getLogger('pymygw')

        '''
            Init MySensor Objects
        '''
        self._MySensorInternal = MySensor.MySensorInternal()
        self._MySensorMessagetype = MySensor.MySensorMessageType()
        self._MySensorPresentation = MySensor.MySensorPresentation()
        self._MySensorSetReq = MySensor.MySensorSetReq(publisher)

        self._serialPort = config.SerialPort
        self._serialBaud = config.SerialBaud
        self._serialTimeOut = config.SerialTimeOut
        self._serialIsConnected = False
        self._serialIsWriteable = False

        self.__connectSerial()
        sleep(5)
        self._cmd = {'nodeid': 0,
                     'childid': 0,
                     'messagetype': self._MySensorMessagetype.id('INTERNAL'),
                     'subtype': self._MySensorInternal.id('I_VERSION'),
                     'payload': 'Get Version'}
        self.__sendSerial()

    def loop(self):
        '''
            Main Loop
        '''
        while self._serialIsConnected:
            try:
                self.response = self._serialConnection.readline()
            except:
                continue
            if self.response:
                self.response = self.response.rstrip(config.EOL)
                self._log.info('incoming message: {0}'.format(self.response))
                self.__parseIncoming()

    def stop(self):
        self._log.info('stop recieved, shutting down')
        self.__disconnectSerial()
        return

    def __parseIncoming(self):
        '''
            Main Worker
            parse incoming serial lines
        '''
        self._splitresponse = self.response.split(config.Seperator, 6)

        if self.__isLongEnough():
            if self.__isDebug():
                self._log.info('Skipping debug message: {0}'.format(self.response))
                return None

            self.__createMessageTemplate()
            n, c, m, a, s, p = self._splitresponse

            self._incomingMessage['nodeid'] = n
            self._incomingMessage['childid'] = c
            self._incomingMessage['messagetype'] = self._MySensorMessagetype.name(m)
            self._incomingMessage['ack'] = a
            self._incomingMessage['subtype'] = self.__toInt(s)
            self._incomingMessage['payload'] = p
            if self.__toInt(m) == self._MySensorMessagetype.id('PRESENTATION'):
                self._processedby = self._MySensorPresentation
            elif self.__toInt(m) == self._MySensorMessagetype.id('SET') or \
                    self.__toInt(m) == self._MySensorMessagetype.id('REQ'):
                self._processedby = self._MySensorSetReq
            elif self.__toInt(m) == self._MySensorMessagetype.id('INTERNAL'):
                self._processedby = self._MySensorInternal
            else:
                self._log.debug('Skipping {0}: unknown messagetype'.format(self._incomingMessage))

            '''
                skip gateway
                address: 0;0
            '''
            if self._incomingMessage['nodeid'] == 0:
                self._log.debug('Skipping Node {0} Message: gw node'.format(n))

            '''
                pass the parsed message to the matching mysensors obj
                returns != None if we need to send a serial message
            '''
            self._cmd = self._processedby.message(self._incomingMessage)
            if self._cmd is not None:
                self.__sendSerial()

    def __createMessageTemplate(self):
        self._incomingMessage = {}
        for k in config.MySensorStructureTemplate:
            self._incomingMessage[k] = None

    def __isDebug(self):
        '''
            Internal ID 3
            SubType ID 9
        '''
        if self._splitresponse[2] == '3' and self._splitresponse[4] == '9':
            return True
        return False

    def __toInt(self, i):
        return int(float(i))

    def __isLongEnough(self):
        self._log.debug('Message Length: {0}, Message: {1}'.format(len(self._splitresponse), self._splitresponse))
        return True if len(self._splitresponse) == 6 else False

    def __prepareCommand(self):
        '''
            prepare the Serial Command
        '''
        for k in config.MySensorStructureTemplate:
            if k not in self._cmd:
                self._cmd[k] = config.MySensorStructureTemplate[k]

        self._serialcmd = '{nodeid}{sep}{childid}{sep}{messagetype}{sep}{ack}{sep}{subtype}{sep}{payload}\n'.format(**self._cmd)

    def __connectSerial(self):
        try:
            self._serialConnection = serial.Serial(self._serialPort,
                                                   self._serialBaud,
                                                   timeout=self._serialTimeOut)
            self._serialConnection.close()
            self._serialConnection.open()
            self._serialIsConnected = True
            self._log.info('serial started up on {0}, Baud {1}, Timeout {2}'.format(self._serialPort,
                                                                                    self._serialBaud,
                                                                                    self._serialTimeOut))
        except Exception, e:
            self._log.error('serial connection failed. {0}'.format(e))
            self._serialIsConnected = False

        if self._serialConnection.writable:
            self._serialIsWriteable = True
            self._log.info('serial is writeable')

    def __disconnectSerial(self):
        if self._serialIsConnected:
            self._serialConnection.close()
            self._log.info('serial connection closed')
            self._serialIsConnected = False

    def __sendSerial(self):
        self.__prepareCommand()
        if self._serialIsConnected and self._serialIsWriteable:
            self._serialConnection.write(self._serialcmd)
            self._log.info('command send: {0}'.format(self._serialcmd))
