from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, UniqueConstraint, ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, reconstructor
from sqlalchemy import orm
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.pool import StaticPool
import time
import json
from logging import getLogger

import Entities
from Entities import Schema, FirmwareType, Firmware, Node, Sensor

import config

class NodeProcessor:
    def __init__(self, node):
        self._node = node

    def process(self, msg):
        '''
            updates the db entry if needed
        '''
        type = msg.getSubType()
        
        if type == config.MySensorInternal['I_BATTERY_LEVEL']:
            self._node.battery = msg.getPayload()
        elif type == config.MySensorInternal['I_SKETCH_NAME']:
            self._node.sketch_name = msg.getPayload()
        elif type == config.MySensorInternal['I_SKETCH_VERSION']:
            self._node.sketch_version = msg.getPayload()
        elif type == config.MySensorInternal['I_VERSION']:
            self._node.api_version = msg.getPayload()
            
        self._node.status = 'Active'
        self._node.requestReboot = False


class SensorProcessor:
    def __init__(self, sensor):
        self._log = getLogger('pymygw')
        self._sensor = sensor

    def process(self, msg):
        '''
            updates the db entry if needed
        '''
        self._sensor.last_seen = time.time()
        
        if msg.isPresentation():
            self._sensor.sensor_type = msg.getSubType()['name'][2:]
        else:
            self._sensor.last_value = msg.getPayload()
        '''
            ToDO: validate SET/REQ-Types with PRESENTATION-Types
        if 'sensortype' in self._args:
            self._args['sensortype'] = self._args['sensortype'].split('_')[1]
            if not self._sensor.sensor_type:
                self._sensor.sensor_type = self._args['sensortype']
            if self._args['sensortype'] != self._sensor.sensor_type:
                self._sensor.sensor_type = self._args['sensortype']
                self._log.debug('SensorType mismatch: DB {0} \n\
                                 Reported Type: {1}'.format(self._sensor.sensor_type,
                                                            self._args['sensortype']))
                #return False
        '''
            

class Database():
    def __init__(self):
        self._log = getLogger('pymygw')
        self._engine = create_engine(config.Database,
                                     #echo=True,
                                     connect_args={'check_same_thread': False},
                                     poolclass=StaticPool)
        self._schema = Entities.getSchema(self._engine)
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
        nodeid = msg.getNodeId()
        processor = None
        if msg.isInternal():
            # node, no sensor
            db_item = self.getNode(nodeid)
            processor = NodeProcessor(db_item)
        else:
            # node and sensor
            db_item = self.getSensor(nodeid, msg.getSensor())
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
    