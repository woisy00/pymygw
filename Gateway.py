import serial
from time import sleep

import config
import MySensor
from pymygw import log


class Gateway(object):
    def __init__(self):
        self._maxNodes = config.MaxNodes
        self._maxChilds = config.MaxChilds
        self._template = config.MySensorStructureTemplate

        '''
            Init MySensor Objects
        '''
        self._internal = MySensor.MySensorInternal()
        self._messagetype = MySensor.MySensorMessageType()
        self._presentation = MySensor.MySensorPresentation()
        self._setreq = MySensor.MySensorSetReq()

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
            response = self._serialConnection.readline()
            if response:
                return response
        return None

    def __prepareCommand(self):
        for k in self._template:
            if k not in self._cmd:
                self._cmd[k] = self._template[k]

        self._serialcmd = '{nodeid}{sep}\
                           {childid}{sep}\
                           {messagetype}{sep}\
                           {ack}{sep}\
                           {subtype}{sep}\
                           {payload}'.format(**self._cmd)

    def __connectSerial(self):
        try:
            self._serialConnection = serial.Serial(self._serialPort,
                                                   self._serialBaud,
                                                   timeout=self._serialTimeOut)
            self._serialConnection.close()
            self._serialConnection.open()
            self._serialIsConnected = True
            log.info('serial started up on {0}, Baud {1}, Timeout {2}'.format(self._serialPort,
                                                                              self._serialBaud,
                                                                              self._serialTimeOut))
        except serial.SerialException, e:
            log.error('serial connection failed. {0}'.format(e))
            self._serialIsConnected = False

        if self._serialConnection.writable:
            self._serialIsWriteable = True
            log.info('serial is writeable')

    def __disconnectSerial(self):
        if self._serialIsConnected:
            self._serialConnection.close()

    def __sendSerial(self):
        self.__prepareCommand()
        if self._serialIsConnected and self._serialIsWriteable:
            self._serialConnection.write(self._serialcmd+config.EOL)
            log.info('command send: {0}'.format(self._serialcmd.strip()))
