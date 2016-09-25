from time import time
from logging import getLogger

import config
import Database
from MQTT import MQTT

log = getLogger('pymygw')
def fromSerial(message):
    splitted = message.split(';', 6)
    if len(splitted) == 6:
        if splitted[2] == '3' and splitted[4] == '9':
            log.info('Skipping debug message: {0}'.format(message))
            return None
            
        n, c, m, a, s, p = splitted
        numericType = int(float(m))
        numericSubType = int(float(s))
        type = None
        subType = None
        
        for nyme, typeDef in config.MySensorMessageType.iteritems():
            if numericType == typeDef['id']:
                type = typeDef
                break
        
        if type is None:
            log.debug('Skipping {0}: unknown messagetype'.format(message))
            return None
        
        for nyme, typeDef in type['subTypes'].iteritems():
            if numericSubType == typeDef['id']:
                subType = typeDef
                break
        if subType is None:
            log.debug('Skipping {0}: unknown subtype'.format(message))
            return None
            
        return Message(n, c, type, subType, p, a==1)
    else:
        return None
        
def fromMQTT(topic, payload):
    # /prefix/in/nodeId/sensor/typeId/subTypeId
    # '/{0}/in/{1}/{2}/{3}/{4}'
    splitted = topic[1:].split('/', 6)
    if len(splitted) == 6:
            
        prefix, direction, nodeId, sensor, type, subType = splitted
        
        if prefix != config.MQTTTopicPrefix:
            return None
        if direction != 'in':
            return None
            
        numericType = int(float(type))
        numericSubType = int(float(subType))
        type = None
        subType = None
        
        for nyme, typeDef in config.MySensorMessageType.iteritems():
            if numericType == typeDef['id']:
                type = typeDef
                break
        
        if type is None:
            log.debug('Skipping {0}: unknown messagetype'.format(message))
            return None
        
        for nyme, typeDef in type['subTypes'].iteritems():
            if numericSubType == typeDef['id']:
                subType = typeDef
                break
        if subType is None:
            log.debug('Skipping {0}: unknown subtype'.format(message))
            return None
            
        return Message(nodeId, sensor, type, subType, payload, True)
    else:
        return None

class Message:
    
    
    def __init__(self, nodeId, sensor, messageType, subType, payload, ack=False):        
        self.__nodeId = nodeId
        self.__sensor = sensor
        self.__messageType = messageType
        self.__subType = subType
        self.__ack = ack
        self.__payload = payload

    def getNodeId(self):
        return self.__nodeId
        
    def getSensor(self):
        return self.__sensor
        
    def getType(self):
        return self.__messageType

    def getTypeId(self):
        return self.__messageType['id']
    
    def getSubType(self):
        return self.__subType

    def getSubTypeId(self):
        return self.__subType['id']
            
    def getPayload(self):
        return self.__payload
    
    def isInternal(self):
        return self.__sensor == 255 or self.__messageType == config.MySensorMessageType['INTERNAL']
        
    def isSet(self):
        return self.__messageType == config.MySensorMessageType['SET']

    def isReq(self):
        return self.__messageType == config.MySensorMessageType['REQ']

    def isPresentation(self):
        return self.__messageType == config.MySensorMessageType['PRESENTATION']

    def isStream(self):
        return self.__messageType == config.MySensorMessageType['STREAM']
        
    def toSerial(self):
        return '{0};{1};{2};{4};{3};{5}\n'.format(self.__nodeId, self.__sensor, 
                        self.__messageType['id'], self.__subType['id'], 1 if self.__ack else 0, self.__payload)
                        
    def toMQTT(self, prefix):
        return '/{0}/out/{1}/{2}/{3}/{4}'.format(prefix, self.__nodeId, self.__sensor, self.__messageType['id'], self.__subType['id'])
    
    def __str__(self):
        return  'nodeid: {0}, childid: {1}, messagetype: {2}, subtype: {3}, ack: {4}, payload: [{5}]'.format(
            self.__nodeId, self.__sensor, self.__messageType['name'], self.__subType['name'], self.__ack, self.__payload)
    
    def __repr__(self):
        return self.__str__()
        
class FirmwareConfigResponse(Message):
    
    def __init__(self, nodeId, payload):
        Message.__init__(self, nodeId, 255, config.MySensorMessageType['STREAM'], 
                config.MySensorStream['ST_FIRMWARE_CONFIG_RESPONSE'], payload)

class FirmwareResponse(Message):
    
    def __init__(self, nodeId, payload):
        Message.__init__(self, nodeId, 255, config.MySensorMessageType['STREAM'], 
                config.MySensorStream['ST_FIRMWARE_RESPONSE'], payload)
                

class RebootMessage(Message):
    
    def __init__(self, nodeId):
        Message.__init__(self, nodeId, 255, config.MySensorMessageType['INTERNAL'], 
                config.MySensorInternal['I_REBOOT'], 'Reboot')
                
class MySensor():
    def __init__(self):
        self._log = getLogger('pymygw')
        '''
            RevertDict id -> Name
        '''
        self.RevertDict = {}
        for k, v in self._dict.iteritems():
            self.RevertDict[v['id']] = k

    def __prepare(self, i, t='str'):
        if t == 'str' and isinstance(i, str):
            self._request = i.upper()
        elif t == 'int':
            self._request = self.__toInt(i)

    def __searchRequest(self):
        self._answer = None
        if self._request in self._dict:
            self._answer = self._dict[self._request][self._lf]

    def __toInt(self, i):
        return int(float(i))

    def process(self):
        # replaced by child process
        raise NotImplementedError()

    def name(self, i):
        self.__prepare(i, t='int')
        if self._request in self.RevertDict:
            return self.RevertDict[self._request]

    def id(self, i):
        self.__prepare(i)
        self._lf = 'id'
        self.__searchRequest()
        return self._answer

    def comment(self, i):
        self.__prepare(i)
        self._lf = 'comment'
        self.__searchRequest()
        return self._answer

    def message(self, m):
        self._response = None
        self._message = m
        self._db = Database.Database2()
        self._log.debug('Parsed Message:\n {0}'.format(m))
        
        self.process()
        if self._response is not None:
            self._log.debug('Created Response: {0}'.format(self._response))
        return self._response
    
    def triggerReboot(self):
        if self._db.isRebootRequested(self._message.getNodeId()):
            self._log.info('Reboot for Node [{0}] requested!'.format(self._message.getNodeId()))
            self._response = Message(self._message.getNodeId(), 255,
                        config.MySensorMessageType['INTERNAL'],
                        config.MySensorInternal['I_REBOOT'],
                        "")
            return True
        else:
            return False


class MySensorMessageType(MySensor):
    '''
        MySensor MessageType Mapping Object
    '''
    def __init__(self):
        self._dict = config.MySensorMessageType
        MySensor.__init__(self)

    def process(self):
        '''TODO'''
        return None


class MySensorPresentation(MySensor):
    '''
        MySensor Presentation Mapping Object
    '''
    def __init__(self):
        self._dict = config.MySensorPresentation
        MySensor.__init__(self)

    def process(self):
        if self._message.getSubTypeId() == self.id('S_ARDUINO_NODE')\
            or self._message.getSubTypeId() == self.id('S_ARDUINO_REPEATER_NODE'):
            # ignore Node presentation!
            return

        self._log.debug('Message in presentation: {0}'.format(self._message))
        self._db.process(self._message)


class MySensorSetReq(MySensor):
    '''
        MySensor Set and Request Mapping Object
    '''
    def __init__(self):
        self._dict = config.MySensorSetReq
        MySensor.__init__(self)

    def process(self):
        if self.triggerReboot():
            return
            
        if self._message.isSet():
            self.__set()

    def __set(self):
        self._log.debug('Message in set: {0}'.format(self._message))
        self._db.process(self._message)
        MQTT.instance.publish(self._message)


class MySensorInternal(MySensor):
    '''
        MySensor Internal Mapping Object
    '''
    def __init__(self):
        self._dict = config.MySensorInternal
        MySensor.__init__(self)

    def process(self):
        self._log.debug('Processing Internal Message')
        
        if self._message.getSubTypeId() == self.id('I_BATTERY_LEVEL'):
            self._log.debug('Message in set: {0}'.format(self._message))
            self._db.process(self._message)
            MQTT.instance.publish(self._message)
        elif self._message.getSubTypeId() == self.id('I_HEARTBEAT'):
            if self.triggerReboot():
                return
        elif self._message.getSubTypeId() == self.id('I_HEARTBEAT_RESPONSE'):
            if self.triggerReboot():
                return
        elif self._message.getSubTypeId() == self.id('I_TIME'):
            if self.triggerReboot():
                return
            self._log.debug('Processed by I_TIME: {0}'.format(self._message))
            self.__GetTime()
        elif self._message.getSubTypeId() == self.id('I_VERSION'):
            self._db.process(self._message)
        elif self._message.getSubTypeId() == self.id('I_ID_REQUEST'):
            self._log.debug('Processed by I_ID_REQUEST: {0}'.format(self._message))
            self.__IDRequest()
        elif self._message.getSubTypeId() == self.id('I_ID_RESPONSE'):
            pass
        elif self._message.getSubTypeId() == self.id('I_INCLUSION_MODE'):
            pass
        elif self._message.getSubTypeId() == self.id('I_CONFIG'):
            self._log.debug('Processed by I_CONFIG: {0}'.format(self._message))
            self.__Config()
        elif self._message.getSubTypeId() == self.id('I_FIND_PARENT'):
            pass
        elif self._message.getSubTypeId() == self.id('I_FIND_PARENT_RESPONSE'):
            pass
        elif self._message.getSubTypeId() == self.id('I_LOG_MESSAGE'):
            pass
        elif self._message.getSubTypeId() == self.id('I_CHILDREN'):
            pass
        elif self._message.getSubTypeId() == self.id('I_SKETCH_NAME'):
            self._log.debug('Processed by I_SKETCH_NAME: {0}'.format(self._message))
            self._db.process(self._message)
        elif self._message.getSubTypeId() == self.id('I_SKETCH_VERSION'):
            self._db.process(self._message)
        elif self._message.getSubTypeId() == self.id('I_REBOOT'):
            pass
        elif self._message.getSubTypeId() == self.id('I_GATEWAY_READY'):
            pass

    def __IDRequest(self):
        '''
            create new id for unknown nodes
            and send it as ID_RESPONSE
        '''
        newID = self._db.newNodeID()
        self._log.debug("new id {0}".format(newID))
        if newID:
            self._response = Message(255, 255,
                     config.MySensorMessageType['INTERNAL'],
                     config.MySensorInternal['I_ID_RESPONSE'], 
                     newID)
            
    def __Config(self):
        '''
            return config
            only used for get_metric afaik
        '''
        self._response = Message(self._message.getNodeId(),
                     255,
                     config.MySensorMessageType['INTERNAL'],
                     config.MySensorInternal['I_CONFIG'], 
                     config.UnitSystem)
                     
    def __GetTime(self):
        self._response = Message(self._message.getNodeId(),
                     self._message.getSensor(),
                     config.MySensorMessageType['INTERNAL'],
                     config.MySensorInternal['I_TIME'], 
                     int(time()))

    def __Sketch_Name(self):
        pass
        
class MySensorStream(MySensor):
    '''
        MySensor Stream Mapping Object
    '''
    def __init__(self):
        self._dict = config.MySensorStream
        MySensor.__init__(self)

    def process(self):
        self._log.debug('Processing Stream Message')

        if self._message.getSubTypeId() == self.id('ST_FIRMWARE_CONFIG_REQUEST'):
            self.__FirmwareConfigReq()
        elif self._message.getSubTypeId() == self.id('ST_FIRMWARE_CONFIG_RESPONSE'):
            pass
        elif self._message.getSubTypeId() == self.id('ST_FIRMWARE_REQUEST'):
            self.__FirmwareReq()
        elif self._message.getSubTypeId() == self.id('ST_FIRMWARE_RESPONSE'):
            pass
        elif self._message.getSubTypeId() == self.id('ST_SOUND'):
            pass
        elif self._message.getSubTypeId() == self.id('ST_IMAGE'):
            pass
        

    def __pullWord(self, pos):
        return int(self._message.getPayload()[pos:pos+2], 16) + 256 * int(self._message.getPayload()[pos+2:pos+4], 16)
    
    def __pushWord(self, arr, val):
        arr.append(val & 0x00FF)
        arr.append((val  >> 8) & 0x00FF)

    def encode(self, payload):
        msg = ""
        for v in payload: 
            if v < 16:
                msg = msg + "0"
            msg = msg + '%x' % v
        return msg

    def __FirmwareConfigReq(self):
        # 0100 0300 3003 FFFF 0101
        # type:     01 00  -> 01 + 00 * 256 -> 1
        # version:  03 00  -> 03 + 00 * 256 -> 3
        # blocks:   30 03  -> 30 + 03 * 256 -> 816
        # crc:      FF FF
        fwtype = self.__pullWord(0)
        fwversion = self.__pullWord(4)
        fwblocks = self.__pullWord(8)
        fwcrc = self.__pullWord(12)
        
        
        nodeId = self._message.getNodeId()
        node = self._db.getNode(nodeId)
        
        if node is None:
            return
            
        if node.firmware_id is None:
            return
            
        fw = self._db.selectFirmware(node.firmware_id)
        
        payload = []
        
        self.__pushWord(payload, fw.type_id)
        self.__pushWord(payload, int(fw.version))
        self.__pushWord(payload, fw.blocks)
        self.__pushWord(payload, int(fw.crc))
        
        if int(fw.version) != fwversion or fw.type_id != fwtype:            
            self._log.info("Node [{0}] needs an update to firmware {1}, Version {2}".format(
                            nodeId, fw.type.name, fw.version))
            node.status = 'Firmware upgrade needed';
            self._db.commit();
        elif int(fw.crc) != fwcrc:
            self._log.info("Node [{0}] needs an update due to a different checksum!".format(nodeId))
            node.status = 'Firmware upgrade needed';
            self._db.commit();
            
        self._response = FirmwareConfigResponse(self._message.getNodeId(), self.encode(payload))

    def __FirmwareReq(self):
        fwtype = self.__pullWord(0)
        fwversion = self.__pullWord(4)
        fwblock = self.__pullWord(8)
        
        self._log.debug('Requesting firmware {0}, Version {1} for node {2}'.format(
                        fwtype, fwversion, self._message.getNodeId()))

        nodeId = self._message.getNodeId()
        node = self._db.getNode(nodeId)
                
        fw = self._db.getFirmware(fwtype, fwversion)
        if fw is not None:
            node.status = 'Sending firmware block {0}/{1}'.format((fw.blocks - fwblock), fw.blocks);
            self._db.commit();
            payload = []
            self.__pushWord(payload, fw.type_id)
            self.__pushWord(payload, int(fw.version))
            self.__pushWord(payload, fwblock)
            for i in range(0, 16):
                block = fwblock * 16 + i
                payload.append(fw.getBlock(block))

            self._response = FirmwareResponse(self._message.getNodeId(), self.encode(payload))
                        