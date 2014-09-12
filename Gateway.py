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
        self._log = log
        
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
            self.response = self._serialConnection.readline()
            if self.response:
                self._log.info('got message: {0}'.format(self.response))
                self.__parseIncomming()
                return self.response
        return None

    def __parseIncomming(self):
        '''
            parse incoming serial lines
        '''
        try:
            n,c,m,s,p = self.response.split(config.Seperator)
        except:
            self._log.error('parse error: {0}'.format(self.response))
            return None
        if p.startswith('read='):
            self._log.debug('get debug message: {0}'.format(self.response))
            return None
            
        self._incoming = self._template
        self._incoming['nodeid'] = n
        self._incoming['childid'] = c
        self._incoming['messagetype'] = self._messagetype(m)
        if int(m) == self._internal.id('PRESENTATION'):
            self._incoming['subtype'] = self._presentation(s)
        elif int(m) == self._internal.id('SET') or int(m) == self._internal.id('REQ'):
            self._incoming['subtype'] = self._setreq(s)
        else:
             self._incoming['subtype'] = s
        self._incoming['payload'] = p
        self._log.debug('NodeID: {nodeid}, ChildID: {childid}, MessageType: {messagetype}, SubType: {subtype}, Payload: {payload}'.format(**self._incoming))
        
        
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

        self._serialcmd = '{nodeid}{sep}{childid}{sep}{messagetype}{sep}{ack}{sep}{subtype}{sep}{payload}'.format(**self._cmd)
        
        
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
            self._serialConnection.write(self._serialcmd+config.EOL)
            self._log.info('command send: {0}'.format(self._serialcmd.strip()))
