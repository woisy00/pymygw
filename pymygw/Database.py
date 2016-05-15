from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, UniqueConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, reconstructor
from sqlalchemy import orm
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.pool import StaticPool
import time
import json
from logging import getLogger

import config
Base = declarative_base()


class Node(Base):
    __tablename__ = 'node'
    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, nullable=False)
    name = Column(String(60), default=None)
    sketch_name = Column(String(60), default=None)
    sketch_version = Column(String(60), default=None)
    api_version = Column(String(20), default=None)
    battery = Column(Integer, default=0)
    battery_level = Column(Float, default=0)
    requestReboot = Column(Boolean, default=False)
    firmware_id = Column(Integer, ForeignKey('firmware.id'))
    firmware = relationship("Firmware")

    def __repr__(self):
        return json.dumps({'Node': self.node_id,
                           'Name': self.name,
                           'Sketch Name': self.sketch_name,
                           'Sketch Version': self.sketch_version,
                           'API Version': self.api_version,
                           'Battery': self.battery,
                           'Battery Level': self.battery_level})


class Sensor(Base):
    __tablename__ = 'sensor'
    id = Column(Integer, primary_key=True)
    name = Column(String(29), default=None)
    node_id = Column(Integer, ForeignKey('node.node_id'), nullable=False)
    sensor_id = Column(Integer, default=0)
    sensor_type = Column(String(20), default=None)
    comment = Column(String(255))
    description = Column(String(255))
    last_seen = Column(Integer, default=0)
    last_value = Column(String(20), default=0)

    node = relationship("Node")
    __table_args__ = (UniqueConstraint('node_id', 'sensor_id'),)

    def __repr__(self):
        return json.dumps({'Node': self.node_id,
                           'Name': self.name,
                           'Sensor': self.sensor_id,
                           'Type': self.sensor_type,
                           'Comment': self.comment,
                           'Description': self.description,
                           'Last Seen': self.last_seen,
                           'Last Value': self.last_value})


class FirmwareType(Base):
    __tablename__ = 'firmware_type'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), default=None, unique=True)
    
    def __repr__(self):
        return json.dumps({'Name': self.name})
                           
class Firmware(Base):
    __tablename__ = 'firmware'
    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey('firmware_type.id'), nullable=False)
    type = relationship("FirmwareType")
    version = Column(String(20), default=None)
    data = Column(String(4000))

    def __repr__(self):
        return json.dumps({'Type': self.type_id,
                           'Version': self.version,
                           'Blocks': self.blocks,
                           'CRC': self.crc,
                           'data': self.data})
    @orm.reconstructor
    def init_on_load(self):
        self.__parse()
        
    def getBlock(self, block):
        return self.__fwdata[block]
    
    def parse(self, type, version, data):
        self.type_id = type.id
        self.version = version
        self.data = data
        self.__parse()
        
    def __parse(self):
        fwdata = []
        start = 0
        end = 0
        pos = 0
        
        for l in self.data.split("\n"):
            line = l.strip()
            if len(line) > 0:
                while line[0:1] != ":":
                    line = line[1:]
                reclen = int(line[1:3], 16)
                offset = int(line[3:7], 16)
                rectype = int(line[7:9], 16)
                data = line[9:9 + 2 * reclen]
                chksum = int(line[9 + (2 * reclen):9 + (2 * reclen) + 2], 16)
                if rectype == 0:
                    if start == 0 and end == 0:
                        if offset % 128 > 0:
                            raise Error("error loading hex file - offset can't be devided by 128")
                        start = offset
                        end = offset

                    if offset < end:
                        raise Error("error loading hex file - offset lower than end")
                    while offset > end:
                        fwdata.append(255)
                        pos = pos + 1
                        end = end + 1
                        
                    for i in range(0, reclen):
                        fwdata.append(int(data[i * 2:(i * 2) + 2], 16))
                        pos = pos + 1
                    end += reclen
        pad = end % 128
        for i in range(0, 128 - pad):
            fwdata.append(255)
            pos = pos + 1
            end = end + 1
        self.blocks = (end - start) / 16
        crc = 0xFFFF
        for i in range(0, self.blocks * 16):
            crc = self.__crc(crc, fwdata[i])

        self.crc = crc
        self.__fwdata = fwdata
        
    def __crc(self, old, data):
        crc = old ^ data
        for bit in range(0, 8):
            if (crc&0x0001) == 0x0001:
                crc = ((crc >> 1) ^ 0xA001)
            else:
                crc = crc >> 1
        return crc
    
class NodeProcessor:
    def __init__(self, node):
        self._node = node

    def process(self, msg):
        '''
            updates the db entry if needed
        '''
        type = msg['sensortype']
        value = msg['payload']
        
        if type == 'I_BATTERY_LEVEL':
            self._node.battery = value
        elif type == 'I_SKETCH_NAME':
            self._node.sketch_name = value
            self._node.requestReboot = False
        elif type == 'I_SKETCH_VERSION':
            self._node.sketch_version = value
        elif type == 'I_VERSION':
            self._node.api_version = value


class SensorProcessor:
    def __init__(self, sensor):
        self._log = getLogger('pymygw')
        self._sensor = sensor

    def process(self, msg):
        '''
            updates the db entry if needed
        '''
        self._args = msg
        self._sensor.last_seen = time.time()
        if 'sensortype' in self._args:
            '''
                strip of first two characters
                could be S_ V_
                depends on presentation or set/req
            '''
            self._args['sensortype'] = self._args['sensortype'].split('_')[1]
            if not self._sensor.sensor_type:
                self._sensor.sensor_type = self._args['sensortype']
            if self._args['sensortype'] != self._sensor.sensor_type:
                self._sensor.sensor_type = self._args['sensortype']
                self._log.debug('SensorType mismatch: DB {0} \n\
                                 Reported Type: {1}'.format(self._sensor.sensor_type,
                                                            self._args['sensortype']))
                #return False

        if 'comment' in self._args and \
                self._args['comment'] != self._sensor.comment:
            self._sensor.comment = self._args['comment']

        if 'description' in self._args and \
                self._args['description'] != self._sensor.description:
            self._sensor.description = self._args['description']


        if 'payload' in self._args and \
                self._args['payload'] != self._sensor.last_value:
            self._sensor.last_value = self._args['payload']

       

class Database2():
    def __init__(self):
        self._log = getLogger('pymygw')
        self._engine = create_engine(config.Database,
                                     connect_args={'check_same_thread': False},
                                     poolclass=StaticPool)
        Base.metadata.create_all(self._engine)
        Base.metadata.bind = self._engine
        self._dbsession = scoped_session(sessionmaker(bind=self._engine))

    def commit(self):
        try:
            self._dbsession.commit()
            self._log.debug('Commit successfull')
            return True
        except Exception, e:
            self._log.error('Commit failed! Exception: {0}'.format(e))
            self._dbsession.rollback()
            return False

    def getNode(self, nodeId):
        try:
            return self._dbsession.query(Node)\
                                    .filter(Node.node_id == nodeId)\
                                    .one()
        except NoResultFound:
            self._log.debug('No DB entry found for Node: {0}'.format(nodeId))
            node = Node(node_id=nodeId, name="")
            self._log.debug('Adding Node {0}'.format(nodeId))
            self._dbsession.add(node)
            self._dbsession.commit()
            return node
        except Exception,e:
            self._log.debug('unknown error when quering for node {}: {}'.format(nodeId, e))

    def getSensor(self, nodeId, sensorId):
        try:
            return self._dbsession.query(Sensor)\
                                  .filter(Sensor.node_id == nodeId,
                                          Sensor.sensor_id == sensorId)\
                                  .one()
        except NoResultFound:
            self._log.debug('No DB entry found for Sensor: {0} on Node: {1}'.format(sensorId, nodeId))
            sensor = Sensor(node_id=nodeId, sensor_id=sensorId, last_seen=time.time(), name="")
            self._log.debug('Adding Sensor {0}/{1}'.format(nodeId, sensorId))
            self._dbsession.add(sensor)
            self._dbsession.commit()
            return sensor
        except Exception,e:
            self._log.debug('unknown error when quering for node {}: {}'.format(nodeId, e))

    def process(self, msg):
        nodeid = msg['nodeid']
        processor = None
        if int(msg['childid']) == 255:
            # node, no sensor
            db_item = self.getNode(nodeid)
            processor = NodeProcessor(db_item)
        else:
            # node and sensor
            db_item = self.getSensor(nodeid, msg['childid'])
            processor = SensorProcessor(db_item)
        processor.process(msg);
        self.commit()


    def newNodeID(self):
        '''
            New sensor node,
            generate new node id and return it
        '''
        lastid = self._dbsession.query(Node.node_id)\
                                .order_by(Node.node_id.desc())\
                                .first()
        self._log.debug('Last DB Node ID: '.format(lastid))
        if lastid is None:
            newid = 1
        else:
            newid = lastid[0] + 1

        newnode = Node(node_id=newid)
        self._log.debug('Adding Node {0}'.format(newid))
        self._dbsession.add(newnode)
        if self.commit():
            self._log.debug('New node added to DB: {0}'.format(newnode))
            return newid
        else:
            self._log.error('Adding node failed: {0}'.format(newnode))
            return False

    def loadSensors(self):
        return self._dbsession.query(Sensor).all()
    
    def loadNodes(self):
        return self._dbsession.query(Node).all()
        
    def loadFirmwares(self):
        return self._dbsession.query(Firmware).all()

    def getFirmwareType(self, name):
        return self._dbsession.query(FirmwareType)\
                                .filter(FirmwareType.name == name)\
                                .one_or_none()

    def getFirmware(self, type, version):
        return self._dbsession.query(Firmware)\
                                .filter(Firmware.type_id == type,
                                        Firmware.version == version)\
                                .one_or_none()
    
    def selectFirmware(self, id):
        return self._dbsession.query(Firmware)\
                                .filter(Firmware.id == id)\
                                .one_or_none()

    def addFirmwareType(self, name):
        fwt = FirmwareType()
        fwt.name = name
        self._dbsession.add(fwt)
        self.commit()                                
        return self._dbsession.query(FirmwareType)\
                                .filter(FirmwareType.name == name)\
                                .one()
                                
    def addFirmware(self, type, version, data):
        fw = self._dbsession.query(Firmware)\
                                .filter(Firmware.type_id == type.id,
                                        Firmware.version == version)\
                                .one_or_none()
        if fw is None:
            fw = Firmware()
            fw.parse(type, version, data)
            self._dbsession.add(fw)
            self._dbsession.flush()
        else:
            fw.parse(type, version, data)
            
        self.commit()
        
    def deleteNode(self, nodeId):
        node = self._dbsession.query(Node)\
                                .filter(Node.node_id == nodeId)\
                                .one()
        sensors = self._dbsession.query(Sensor)\
                                .filter(Sensor.node_id == nodeId)\
                                .all()
        for sensor in sensors:
            self._dbsession.delete(sensor)
        
        self._dbsession.delete(node)
        self.commit()
    
    def isRebootRequested(self, nodeId):
        node = self._dbsession.query(Node)\
                                .filter(Node.node_id == nodeId)\
                                .one_or_none()
        if node is not None:
            return node.requestReboot
        else:
            return False
    