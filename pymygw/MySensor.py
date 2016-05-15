from time import time
from logging import getLogger

import config
import Database

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
        self._cmd = None
        self._message = m
        self._db = Database.Database2()
        self._log.debug('Parsed Message:\n\
                         \tNodeID: {0},\n\
                         \tChildID: {1},\n\
                         \tMessageType: {2},\n\
                         \tSubType: {3},\n\
                         \tPayload: {4}'.format(self._message['nodeid'],
                                                self._message['childid'],
                                                self._message['messagetype'],
                                                self.name(self._message['subtype']),
                                                self._message['payload']))
        
        self.process()
        if self._cmd is not None:
            self._log.debug('Created CMD: {0}'.format(self._cmd))
        return self._cmd
    
    def triggerReboot(self):
        if self._db.isRebootRequested(self._message['nodeid']):
            self._log.info('Reboot for Node [{0}] requested!'.format(self._message['nodeid']))
            self._cmd = {'nodeid': self._message['nodeid'],
                        'childid': 255,
                        'messagetype': config.MySensorMessageType['INTERNAL']['id'],
                        'subtype': config.MySensorInternal['I_REBOOT']['id'],
                        'payload': ''}
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
        return self._cmd


class MySensorPresentation(MySensor):
    '''
        MySensor Presentation Mapping Object
    '''
    def __init__(self):
        self._dict = config.MySensorPresentation
        MySensor.__init__(self)

    def process(self):
        if self.triggerReboot():
            return

        self._message['sensortype'] = self.name(self._message['subtype'])
        self._message['comment'] = self.comment(self.name(self._message['subtype']))
        self._message['description'] = self._message['payload']
        # When it is a presentation message, 
        # we don't need to update the latest value
        # del (self._message['payload'])
        self._log.debug('Message in presentation: {0}'.format(self._message))
        
        self._db.process(self._message)


class MySensorSetReq(MySensor):
    '''
        MySensor Set and Request Mapping Object
    '''
    def __init__(self, publisher):
        self._dict = config.MySensorSetReq
        MySensor.__init__(self)
        self._publisher = publisher

    def process(self):
        if self.triggerReboot():
            return
            
        if self._message['messagetype'] == 'SET':
            self.__set()

    def __set(self):
        self._message['sensortype'] = self.name(self._message['subtype'])
        self._log.debug('Message in set: {0}'.format(self._message))
        self._db.process(self._message)
        db_info = self._db.getSensor(self._message['nodeid'], self._message['childid'])
        self._publisher.publishSensorValue(self._message, db_info)


class MySensorInternal(MySensor):
    '''
        MySensor Internal Mapping Object
    '''
    def __init__(self, publisher):
        self._dict = config.MySensorInternal
        MySensor.__init__(self)
        self._publisher = publisher

    def process(self):
        self._log.debug('Processing Internal Message')
        self._messagetype = config.MySensorMessageType['INTERNAL']['id']
        self._message['sensortype'] = self.name(self._message['subtype'])

        if self._message['subtype'] == self.id('I_BATTERY_LEVEL'):
            if self.triggerReboot():
                return
            self._log.debug('Message in set: {0}'.format(self._message))
            self._db.process(self._message)
            db_info = self._db.getNode(self._message['nodeid'])
            self._publisher.publishInternalValue(self._message, db_info)
        elif self._message['subtype'] == self.id('I_TIME'):
            if self.triggerReboot():
                return
            self._log.debug('Processed by I_TIME: {0}'.format(self._message))
            self.__GetTime()
        elif self._message['subtype'] == self.id('I_VERSION'):
            self._db.process(self._message)
        elif self._message['subtype'] == self.id('I_ID_REQUEST'):
            self._log.debug('Processed by I_ID_REQUEST: {0}'.format(self._message))
            self.__IDRequest()
        elif self._message['subtype'] == self.id('I_ID_RESPONSE'):
            pass
        elif self._message['subtype'] == self.id('I_INCLUSION_MODE'):
            pass
        elif self._message['subtype'] == self.id('I_CONFIG'):
            self._log.debug('Processed by I_CONFIG: {0}'.format(self._message))
            self.__Config()
        elif self._message['subtype'] == self.id('I_FIND_PARENT'):
            pass
        elif self._message['subtype'] == self.id('I_FIND_PARENT_RESPONSE'):
            pass
        elif self._message['subtype'] == self.id('I_LOG_MESSAGE'):
            pass
        elif self._message['subtype'] == self.id('I_CHILDREN'):
            pass
        elif self._message['subtype'] == self.id('I_SKETCH_NAME'):
            self._log.debug('Processed by I_SKETCH_NAME: {0}'.format(self._message))
            self._db.process(self._message)
        elif self._message['subtype'] == self.id('I_SKETCH_VERSION'):
            self._db.process(self._message)
        elif self._message['subtype'] == self.id('I_REBOOT'):
            pass
        elif self._message['subtype'] == self.id('I_GATEWAY_READY'):
            pass

    def __IDRequest(self):
        '''
            create new id for unknown nodes
            and send it as ID_RESPONSE
        '''
        newID = self._db.newNodeID()
        self._log.debug("new id {0}".format(newID))
        if newID:
            self._cmd = {'nodeid': 255,
                         'childid': 255,
                         'messagetype': self._messagetype,
                         'subtype': self.id('I_ID_RESPONSE'),
                         'payload': newID}

    def __Config(self):
        '''
            return config
            only used for get_metric afaik
        '''
        self._cmd = {'nodeid': self._message['nodeid'],
                     'childid': 255,
                     'messagetype': self._messagetype,
                     'subtype': self.id('I_CONFIG'),
                     'payload': config.UnitSystem}

    def __GetTime(self):
        self._cmd = {'nodeid': self._message['nodeid'],
                     'childid': self._message['childid'],
                     'messagetype': self._messagetype,
                     'subtype': self.id('I_TIME'),
                     'payload': int(time())}

    def __Sketch_Name(self):
        pass
        
class MySensorStream(MySensor):
    '''
        MySensor Stream Mapping Object
    '''
    def __init__(self, publisher):
        self._dict = config.MySensorStream
        MySensor.__init__(self)
        self._publisher = publisher

    def process(self):
        self._log.debug('Processing Stream Message')
        self._messagetype = config.MySensorMessageType['STREAM']['id']
        self._message['sensortype'] = self.name(self._message['subtype'])

        if self._message['subtype'] == self.id('ST_FIRMWARE_CONFIG_REQUEST'):
            self.__FirmwareConfigReq()
        elif self._message['subtype'] == self.id('ST_FIRMWARE_CONFIG_RESPONSE'):
            pass
        elif self._message['subtype'] == self.id('ST_FIRMWARE_REQUEST'):
            self.__FirmwareReq()
        elif self._message['subtype'] == self.id('ST_FIRMWARE_RESPONSE'):
            pass
        elif self._message['subtype'] == self.id('ST_SOUND'):
            pass
        elif self._message['subtype'] == self.id('ST_IMAGE'):
            pass
        

    def __pullWord(self, pos):
        return int(self._message['payload'][pos:pos+2], 16) + 256 * int(self._message['payload'][pos+2:pos+4], 16)
    
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
        
        
        nodeId = self._message['nodeid']
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
        elif int(fw.crc) != fwcrc:
            self._log.info("Node [{0]}] needs an update due to a different checksum!".format(nodeId))
            
        self._cmd = {'nodeid': self._message['nodeid'],
                     'childid': 255,
                     'messagetype': self._messagetype,
                     'subtype': self.id('ST_FIRMWARE_CONFIG_RESPONSE'),
                     'payload': self.encode(payload)}

    def __FirmwareReq(self):
        fwtype = self.__pullWord(0)
        fwversion = self.__pullWord(4)
        fwblock = self.__pullWord(8)
        
        self._log.debug('Requesting firmware {0}, Version {1} for node {2}'.format(
                        fwtype, fwversion, self._message['nodeid']))
                        
        fw = self._db.getFirmware(fwtype, fwversion)
        if fw is not None:
            payload = []
            self.__pushWord(payload, fw.type_id)
            self.__pushWord(payload, int(fw.version))
            self.__pushWord(payload, fwblock)
            for i in range(0, 16):
                block = fwblock * 16 + i
                payload.append(fw.getBlock(block))

            self._cmd = {'nodeid': self._message['nodeid'],
                        'childid': 255,
                        'messagetype': self._messagetype,
                        'subtype': self.id('ST_FIRMWARE_RESPONSE'),
                        'payload': self.encode(payload)}
                        
#function sendFirmwareResponse(destination, fwtype, fwversion, fwblock, db, gw) {
#							var fwtype = pullWord(payload, 0);
#							var fwversion = pullWord(payload, 2);
#							var fwblock = pullWord(payload, 4);
#	db.collection('firmware', function(err, c) {
#		c.findOne({
#			'type': fwtype,
#			'version': fwversion
#		}, function(err, result) {
#			if (err)
#				console.log('Error finding firmware version ' + fwversion + ' for type ' + fwtype);
#			var payload = [];
#			pushWord(payload, result.type);
#			pushWord(payload, result.version);
#			pushWord(payload, fwblock);
#			for (var i = 0; i < FIRMWARE_BLOCK_SIZE; i++)
#				payload.push(result.data[fwblock * FIRMWARE_BLOCK_SIZE + i]);
#			var sensor = NODE_SENSOR_ID;
#			var command = C_STREAM;
#			var acknowledge = 0; // no ack
#			var type = ST_FIRMWARE_RESPONSE;
#			var td = encode(destination, sensor, command, acknowledge, type, payload);
#			console.log('-> ' + td.toString());
#			gw.write(td);
#		});
#	});

        
#const FIRMWARE_BLOCK_SIZE	= 16;
#function pullWord(arr, pos) {
#	return arr[pos] + 256 * arr[pos + 1];
#}
#function pushDWord(arr, val) {
#	arr.push(val & 0x000000FF);
#	arr.push((val  >> 8) & 0x000000FF);
#	arr.push((val  >> 16) & 0x000000FF);
#	arr.push((val  >> 24) & 0x000000FF);
#}
#
#IN:
#
#		case C_STREAM:
#			switch (type) {
#					case ST_FIRMWARE_CONFIG_REQUEST:
#							var fwtype = pullWord(payload, 0);
#							var fwversion = pullWord(payload, 2);
#							sendFirmwareConfigResponse(sender, fwtype, fwversion, db, gw);
#							break;
#					case ST_FIRMWARE_CONFIG_RESPONSE:
#							break;
#					case ST_FIRMWARE_REQUEST:
#							sendFirmwareResponse(sender, fwtype, fwversion, fwblock, db, gw);
#							break;
#                         
#                            
#OUT:
#

#
#function sendFirmwareResponse(destination, fwtype, fwversion, fwblock, db, gw) {
#	db.collection('firmware', function(err, c) {
#		c.findOne({
#			'type': fwtype,
#			'version': fwversion
#		}, function(err, result) {
#			if (err)
#				console.log('Error finding firmware version ' + fwversion + ' for type ' + fwtype);
#			var payload = [];
#			pushWord(payload, result.type);
#			pushWord(payload, result.version);
#			pushWord(payload, fwblock);
#			for (var i = 0; i < FIRMWARE_BLOCK_SIZE; i++)
#				payload.push(result.data[fwblock * FIRMWARE_BLOCK_SIZE + i]);
#			var sensor = NODE_SENSOR_ID;
#			var command = C_STREAM;
#			var acknowledge = 0; // no ack
#			var type = ST_FIRMWARE_RESPONSE;
#			var td = encode(destination, sensor, command, acknowledge, type, payload);
#			console.log('-> ' + td.toString());
#			gw.write(td);
#		});
#	});
#}
