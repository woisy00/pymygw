import serial
from time import sleep
import logging

import config
import MySensor


class Gateway(object):
    def __init__(self, db, openhab):
        self._maxNodes = config.MaxNodes
        self._maxChilds = config.MaxChilds
        self._template = config.MySensorStructureTemplate
        self._log = logging.getLogger('pymygw')
        self._db = db
        self._dbresult = None

        '''
            Init MySensor Objects
        '''
        self._internal = MySensor.MySensorInternal()
        self._messagetype = MySensor.MySensorMessageType()
        self._presentation = MySensor.MySensorPresentation()
        self._setreq = MySensor.MySensorSetReq(openhab)

        self._serialPort = config.SerialPort
        self._serialBaud = config.SerialBaud
        self._serialTimeOut = config.SerialTimeOut
        self._serialIsConnected = False
        self._serialIsWriteable = False

        self.__connectSerial()
        sleep(5)
        self._cmd = {'nodeid': 0,
                     'childid': 0,
                     'messagetype': self._messagetype.id('INTERNAL'),
                     'subtype': self._internal.id('I_VERSION'),
                     'payload': 'Get Version'}
        self.__sendSerial()

    def loop(self):
        '''
            Main Loop
        '''
        if self._serialIsConnected:
            try:
                self.response = self._serialConnection.readline()
            except:
                return None
            if self.response:
                self.response = self.response.rstrip(config.EOL)
                self._log.info('incoming message: {0}'.format(self.response))
                self.__parseIncoming()
                return self.response
        return None

    def stop(self):
        self._db.disconnect()
        self.__disconnectSerial()

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

            self._incoming = self._template
            n, c, m, a, s, p = self._splitresponse

            self._incoming['nodeid'] = n
            self._incoming['childid'] = c
            self._incoming['messagetype'] = self._messagetype.name(m)
            self._incoming['ack'] = a
            self._incoming['subtype'] = self.__toInt(s)
            self._incoming['payload'] = p
            if self.__toInt(m) == self._messagetype.id('PRESENTATION'):
                self._processby = self._presentation
            elif self.__toInt(m) == self._messagetype.id('SET') or \
                    self.__toInt(m) == self._messagetype.id('REQ'):
                self._processby = self._setreq
            elif self.__toInt(m) == self._messagetype.id('INTERNAL'):
                self._processby = self._internal
            else:
                self._log.debug('Skipping {0}: unknown messagetype'.format(self._incoming))
                return

            # pass the parsed message to the matching mysensors obj
            # returns != False if we need to send a serial message
            '''
                skip gateway
                address: 0;0
            '''
            if self._incoming['nodeid'] == 0:
                self._log.debug('Skipping Node {0} Message: gw node'.format(n))
                return None

            self._cmd = self._processby.message(self._incoming, self._db)
            if self._cmd is not None:
                self.__sendSerial()

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

    def __knownNodeChild(self):
        '''
            TODO
            Check sqlite if Node;Sensor is known and glued to openhab stuff
        '''
        pass

    def __prepareCommand(self):
        '''
            prepare the Serial Command
        '''
        for k in self._template:
            if k not in self._cmd:
                self._cmd[k] = self._template[k]

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
        except serial.SerialException, e:
            self._log.error('serial connection failed. {0}'.format(e))
            self._serialIsConnected = False

        if self._serialConnection.writable:
            self._serialIsWriteable = True
            self._log.info('serial is writeable')

    def __disconnectSerial(self):
        if self._serialIsConnected:
            self._serialConnection.close()

    def __sendSerial(self):
        self.__prepareCommand()
        if self._serialIsConnected and self._serialIsWriteable:
            self._serialConnection.write(self._serialcmd)
            self._log.info('command send: {0}'.format(self._serialcmd))
