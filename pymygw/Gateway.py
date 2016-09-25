import serial
from threading import Thread
from time import sleep
from logging import getLogger

import config
import MySensor
from MySensor import Message
import Queue

class MessageQueue:

    def __init__(self, size):
        self._storage = Queue.Queue(size)

    def get(self, timeout):
        try:
            return self._storage.get(True, timeout)
        except Queue.Empty:
            return None
            
    def put(self, o):
        self._storage.put(o)
    
    def task_done(self):
        self._storage.task_done()
    
    def join(self):
        self._storage.join()
        
class SerialConnection:
    
    def __init__(self):
        self._log = getLogger('pymygw')
        
        self._serialPort = config.SerialPort
        self._serialBaud = config.SerialBaud
        self._serialTimeOut = config.SerialTimeOut
        self._serialIsConnected = False
        self._serialIsWriteable = False

    def connect(self):
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
            
        sleep(5)

    def disconnect(self):
        if self._serialIsConnected:
            self._serialIsConnected = False
            self._serialConnection.close()
            self._log.info('serial connection closed')
        
    def readLine(self):
        line = self._serialConnection.readline()
        if line is not None:
            line = line.rstrip(config.EOL)
            
        return line
            
    def write(self, data):
        if self._serialIsWriteable:
            self._serialConnection.write(data)
            self._log.debug('command send: {0}'.format(data))
            
    def isConnected(self):
        return self._serialIsConnected

        
class Reader(Thread):

    def __init__(self, serialConnection, publishQueue):
        self._log = getLogger('pymygw')
        Thread.__init__(self)
        self.daemon = True
        self._stopRequest = False
        self._serialConnection = serialConnection
        self._publishQueue = publishQueue

        '''
            Init MySensor Objects
        '''
        self._MySensorInternal = MySensor.MySensorInternal()
        self._MySensorMessagetype = MySensor.MySensorMessageType()
        self._MySensorPresentation = MySensor.MySensorPresentation()
        self._MySensorSetReq = MySensor.MySensorSetReq()
        self._MySensorStream = MySensor.MySensorStream()

    def run(self):
        '''
            Main Loop
        '''
        while not self._stopRequest and self._serialConnection.isConnected():
            try:
                line = self._serialConnection.readLine()
                if len(line) == 0:
                    continue
                    
                message = MySensor.fromSerial(line)

                if message is None:
                    self._log.info('Skipping message: {0}'.format(line))
                elif message.getNodeId() == 0:
                    self._log.debug('Skipping Node 0 Message: gw node')
                else:
                    if message.isInternal():
                        processedBy = self._MySensorInternal
                    elif message.isPresentation():
                        processedBy = self._MySensorPresentation
                    elif message.isSet() or message.isReq():
                        processedBy = self._MySensorSetReq
                    elif message.isStream():
                        processedBy = self._MySensorStream
                    else:
                        self._log.debug('Skipping {0}: unknown messagetype'.format(self._incomingMessage))
                        return

                    '''
                        pass the parsed message to the matching mysensors obj
                        returns != None if we need to send a serial message
                    '''
                    response = processedBy.message(message)
                    if response is not None:
                        self._publishQueue.put(response)
            except:
                self._log.exception('exception in mainloop')
                
    def stop(self):
        self._stopRequest = True
        self.join()
        
    def __createMessageTemplate(self):
        incomingMessage = {}
        for k in config.MySensorStructureTemplate:
            incomingMessage[k] = None
        return incomingMessage

    def __isDebug(self, message):
        '''
            Internal ID 3
            SubType ID 9
        '''
        if message[2] == '3' and message[4] == '9':
            return True
        return False

    def __toInt(self, i):
        return int(float(i))

    def __isLongEnough(self, message):
        self._log.debug('Message Length: {0}, Message: {1}'.format(len(message), message))
        return True if len(message) == 6 else False


class Writer(Thread):

    def __init__(self, serialConnection, publishQueue):
        self._log = getLogger('pymygw')
        Thread.__init__(self)
        self._serialConnection = serialConnection
        self.daemon = True
        self._publishQueue = publishQueue
        self._stopRequest = False

    def run(self):
        '''
            Main Loop
        '''
        while not self._stopRequest:
            try:
                message = self._publishQueue.get(5)
                if message is not None:
                    self._log.debug('Writing messge to serial: {0}'.format(message))
                    self._serialConnection.write(message.toSerial())
                    self._publishQueue.task_done()
            except:
                self._log.exception('exception in mainloop')
                
    def stop(self):
        # wait until all messages are written
        self._publishQueue.join()
        self._stopRequest = True

        
class Gateway():
    instance = None
    
    def __init__(self):
        self._log = getLogger('pymygw')
        self._messageQueue = MessageQueue(20)
        self._started = False
        
        self._serialConnection = SerialConnection()
            
    def stop(self):
        if self._started:
            self._started = False            
            self._log.info('stop recieved, shutting down')
            # stop reader first
            self._reader.stop()
            # stop writer (blocks until all queued messages
            # are processed)
            self._writer.stop()            
            self._serialConnection.disconnect()

    def start(self):
        if not self._started:
            self._started = True
            self._serialConnection.connect()

            self._reader = Reader(self._serialConnection, self._messageQueue)
            self._writer = Writer(self._serialConnection, self._messageQueue)

            self._writer.start()
            self._messageQueue.put(Message(0, 0, 
                    config.MySensorMessageType['INTERNAL'],
                    config.MySensorInternal['I_VERSION'],
                    'Get Version'))
            self._reader.start()
            
    def writeMessage(self, message):
        if self._started:
            self._messageQueue.put(message)
            