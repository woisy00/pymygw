from sqlalchemy import create_engine, Column, Integer, Float, String, UniqueConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
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
    sketch_name = Column(String(60), default=None)
    sketch_version = Column(String(60), default=None)
    api_version = Column(String(20), default=None)
    battery = Column(Integer, default=0)
    battery_level = Column(Float, default=0)

    sensors = relationship('Sensor', backref='node')

    def __repr__(self):
        return json.dumps({'Node': self.node_id,
                           'Sketch Name': self.sketch_name,
                           'Sketch Version': self.sketch_version,
                           'API Version': self.api_version,
                           'Battery': self.battery,
                           'Battery Level': self.battery_level})


class Sensor(Base):
    __tablename__ = 'sensor'
    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey('node.node_id'), nullable=False)
    sensor_id = Column(Integer, default=0)
    sensor_type = Column(String(20), default=None)
    openhab = Column(String(90), unique=True, nullable=True)
    comment = Column(String(255))
    description = Column(String(255))
    last_seen = Column(Integer, default=0)
    last_value = Column(String(20), default=0)

    __table_args__ = (UniqueConstraint('node_id', 'sensor_id'),)

    def __repr__(self):
        return json.dumps({'Node': self.node_id,
                           'Sensor': self.sensor_id,
                           'Type': self.sensor_type,
                           'Openhab': self.openhab,
                           'Comment': self.comment,
                           'Description': self.description,
                           'Last Seen': self.last_seen,
                           'Last Value': self.last_value})


class NodeProcessor:
    def __init__(self, node):
        self._node = node

    def process(self, msg):
        '''
            updates the db entry if needed
        '''

        self._args = msg
        if 'battery' in self._args and \
                self._args['battery'] != self._node.battery:
            self._node.battery = self._args['battery']

        if 'battery_level' in self._args and \
                self._args['battery_level'] != self._node.battery_level:
            self._node.battery_level = self._args['battery_level']

        if 'api_version' in self._args and \
                self._args['api_version'] != self._node.api_version:
            self._node.api_version = self._args['api_version']

        if 'sketch_version' in self._args and \
                self._args['sketch_version'] != self._node.sketch_version:
            self._node.sketch_version = self._args['sketch_version']

        if 'sketch_name' in self._args and \
                self._args['sketch_name'] != self._node.sketch_name:
            self._node.sketch_name = self._args['sketch_name']


class SensorProcessor:
    def __init__(self, sensor):
        self._log = getLogger('pymygw')
        self._sensor = sensor

    def process(self, msg):
        '''
            updates the db entry if needed
        '''
        self._args = msg
        self.last_seen = time.time()
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
                self._log.error('SensorType mismatch: DB {0} \n\
                                 Reported Type: {1}'.format(self._sensor.sensor_type,
                                                            self._args['sensortype']))
                return False

        if 'openhab' in self._args and \
                self._args['openhab'] != self._sensor.openhab:
            self._log.debug('OpenhabDB entry mismatch: DB {0} \n\
                             New Openhab: {1}'.format(self._sensor.openhab,
                                                      self._args['openhab']))
            self._sensor.openhab = self._args['openhab']

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
        self._result = False

    def __commit(self):
        try:
            self._dbsession.commit()
            self._log.debug('Commit successfull')
            return True
        except Exception, e:
            self._log.error('Commit failed! Exception: {0}'.format(e))
            self._dbsession.rollback()
            return False

    def __get(self, n, s):
        if n and s:
            self.__getSensor(n, s)
        elif n:
            self.__getNode(n)

    def __getNode(self, n):
        self._result = False
        try:
            self._result = self._dbsession.query(Node)\
                                          .filter(Node.node_id == n)\
                                          .one()
        except NoResultFound:
            self._log.debug('No DB entry found for Node: {0}'.format(n))
        except Exception,e:
            self._log.debug('unknown error when quering for node {}: {}'.format(n, e))

    def __getSensor(self, n, s):
        try:
            self._result = self._dbsession.query(Sensor)\
                                          .filter(Sensor.node_id == n,
                                                  Sensor.sensor_id == s)\
                                          .one()
        except NoResultFound:
            self._result = False
            self._log.debug('No DB entry found for Sensor: {0} on Node: {1}'.format(s, n))
        except Exception,e:
            self._log.debug('unknown error when quering for node {}: {}'.format(n, e))

    def __update(self):
        '''
            updates the db entry if needed
        '''
        self._result.last_seen = time.time()
        if 'sensortype' in self._args:
            '''
                strip of first two characters
                could be S_ V_
                depends on presentation or set/req
            '''
            self._args['sensortype'] = self._args['sensortype'].split('_')[1]
            if not self._result.sensor_type:
                self._result.sensor_type = self._args['sensortype']
            if self._args['sensortype'] != self._result.sensor_type:
                self._log.error('SensorType mismatch: DB {0} \n\
                                 Reported Type: {1}'.format(self._result.sensor_type,
                                                            self._args['sensortype']))
                return False

        if 'openhab' in self._args and \
                self._args['openhab'] != self._result.openhab:
            self._log.debug('OpenhabDB entry mismatch: DB {0} \n\
                             New Openhab: {1}'.format(self._result.openhab,
                                                      self._args['openhab']))
            self._result.openhab = self._args['openhab']

        if 'comment' in self._args and \
                self._args['comment'] != self._result.comment:
            self._result.comment = self._args['comment']

        if 'battery' in self._args and \
                self._args['battery'] != self._result.battery:
            self._result.battery = self._args['battery']

        if 'battery_level' in self._args and \
                self._args['battery_level'] != self._result.battery_level:
            self._result.battery_level = self._args['battery_level']

        if 'api_version' in self._args and \
                self._args['api_version'] != self._result.api_version:
            self._result.api_version = self._args['api_version']

        if 'sketch_version' in self._args and \
                self._args['sketch_version'] != self._result.sketch_version:
            self._result.sketch_version = self._args['sketch_version']

        if 'sketch_name' in self._args and \
                self._args['sketch_name'] != self._result.sketch_name:
            self._result.sketch_name = self._args['sketch_name']

        if 'payload' in self._args and \
                self._args['payload'] != self._result.last_value:
            self._result.last_value = self._args['payload']

        if self.__commit():
            self._log.debug('Update for {0} '
                            'finished successfully'.format(self._result))
            return True
        else:
            self._log.error('Updated failed for {0}'.format(self._result))
            return False

    def process(self, msg):
        nodeid = msg['nodeid']
        processor = None
        if int(msg['childid']) == 255:
            # node, no sensor
            db_item = self.get(node = nodeid)
            if type(db_item) is list:
                db_item = db_item[0]
            if not(db_item):
                db_item = Node(node_id=nodeid)
                self._dbsession.add(db_item)
            processor = NodeProcessor(db_item)
        else:
            # node and sensor
            db_item = self.get(node = nodeid, sensor = msg['childid'])
            if type(db_item) is list:
                db_item = db_item[0]
            if not(db_item): 
                db_item = Sensor(node_id=nodeid,
                               sensor_id=msg['childid'],
                               last_seen=time.time())
                self._dbsession.add(db_item)
            processor = SensorProcessor(db_item)
        processor.process(msg);
        self.__commit()



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
        self._dbsession.add(newnode)
        if self.__commit():
            self._log.debug('New node added to DB: {0}'.format(newnode))
            return newid
        else:
            self._log.error('Adding node failed: {0}'.format(newnode))
            return False

    def get(self, node=False, sensor=False):
        self.__get(node, sensor)
        return self._result;# if self._result else self._dbsession.query(Node).all()


class Database():
    def __init__(self):
        self._log = getLogger('pymygw')
        self._engine = create_engine(config.Database,
                                     connect_args={'check_same_thread': False},
                                     poolclass=StaticPool)
        Base.metadata.create_all(self._engine)
        Base.metadata.bind = self._engine
        self._dbsession = scoped_session(sessionmaker(bind=self._engine))
        self._result = False

    def __getbyNode(self, n):
        try:
            self._result = self._dbsession.query(Sensor)\
                                          .filter(Sensor.node_id == n)\
                                          .all()
        except NoResultFound:
            self._result = False
            self._log.debug('No DB entry found for Node: {0}'.format(n))

    def __getbySensorandNode(self, n, s):
        try:
            self._result = self._dbsession.query(Sensor)\
                                          .filter(Sensor.node_id == n,
                                                  Sensor.sensor_id == s)\
                                          .one()
        except NoResultFound:
            self._result = False
            self._log.debug('No DB entry found for Node: {0} Sensor; {1}'.format(n, s))

    def __commit(self):
        try:
            self._dbsession.commit()
            self._log.debug('Commit successfull')
            return True
        except Exception, e:
            self._log.error('Commit failed! Exception: {0}'.format(e))
            self._dbsession.rollback()
            return False

    def __update(self):
        '''
            updates the db entry if needed
        '''
        self._result.last_seen = time.time()
        if 'sensortype' in self._args:
            '''
                strip of first two characters
                could be S_ V_
                depends on presentation or set/req
            '''
            self._args['sensortype'] = self._args['sensortype'].split('_')[1]
            if not self._result.sensor_type:
                self._result.sensor_type = self._args['sensortype']
            if self._args['sensortype'] != self._result.sensor_type:
                self._log.error('SensorType mismatch: DB {0} \n\
                                 Reported Type: {1}'.format(self._result.sensor_type,
                                                            self._args['sensortype']))
                return False

        if 'openhab' in self._args and \
                self._args['openhab'] != self._result.openhab:
            self._log.debug('OpenhabDB entry mismatch: DB {0} \n\
                             New Openhab: {1}'.format(self._result.openhab,
                                                      self._args['openhab']))
            self._result.openhab = self._args['openhab']

        if 'comment' in self._args and \
                self._args['comment'] != self._result.comment:
            self._result.comment = self._args['comment']

        if 'battery' in self._args and \
                self._args['battery'] != self._result.battery:
            self._result.battery = self._args['battery']

        if 'battery_level' in self._args and \
                self._args['battery_level'] != self._result.battery_level:
            self._result.battery_level = self._args['battery_level']

        if 'api_version' in self._args and \
                self._args['api_version'] != self._result.api_version:
            self._result.api_version = self._args['api_version']

        if 'sketch_version' in self._args and \
                self._args['sketch_version'] != self._result.sketch_version:
            self._result.sketch_version = self._args['sketch_version']

        if 'sketch_name' in self._args and \
                self._args['sketch_name'] != self._result.sketch_name:
            self._result.sketch_name = self._args['sketch_name']

        if 'payload' in self._args and \
                self._args['payload'] != self._result.last_value:
            self._result.last_value = self._args['payload']

        if self.__commit():
            self._log.debug('Update for {0} '
                            'finished successfully'.format(self._result))
            return True
        else:
            self._log.error('Updated failed for {0}'.format(self._result))
            return False

    def newID(self):
        '''
            New sensor node,
            generate new node id and return it
        '''
        lastid = self._dbsession.query(Sensor.node_id)\
                                .order_by(Sensor.node_id.desc())\
                                .first()
        self._log.debug('Last DB ID: '.format(lastid))
        if lastid is None:
            newid = 1
        else:
            newid = lastid[0] + 1
        newnode = Sensor(node_id=newid,
                         sensor_id=0,
                         last_seen=time.time())
        self._dbsession.add(newnode)
        if self.__commit():
            self._log.debug('New node added to DB: {0}'.format(newnode))
            return newid
        else:
            self._log.error('Adding node failed: {0}'.format(newnode))
            return False

    def process(self, msg):
        self._args = msg
        if 'nodeid' not in self._args:
            self._log.error('nodeid not found: {0}'.format(self._args))
            return False
        if 'childid' not in self._args:
            self._log.debug('childid not found: {0}'.format(self._args))
            self._args['childid'] = 0
        if int(self._args['childid']) == 255:
            self._log.debug('skipping childid 255')
            return
        self.__getbySensorandNode(self._args['nodeid'], self._args['childid'])
        if self._result:
            '''
                Node + Sensor is known
                update entry
            '''
            self.__update()
        else:
            '''
                Node + Sensor is unknown
                check if new sensor or new node
            '''
            self.__getbySensorandNode(self._args['nodeid'], 0)
            if self._result:
                '''
                    node is known, sensor 0 is always created
                '''
                nid = self._result.node_id
                self._log.info('adding new sensor')
            else:
                '''
                    Node is unknown but it offers an id (old Node/Sensor)
                '''
                nid = self._args['nodeid']
                self._log.info('adding old Node/Sensor')

            newsensor = Sensor(node_id=nid,
                               sensor_id=self._args['childid'],
                               last_seen=time.time())
            self._dbsession.add(newsensor)
            if self.__commit():
                self._log.info('Sensor {0} added on'
                               'Node {1}'.format(self._args['childid'],
                                                 nid))
            else:
                self._log.error('Adding Sensor {0} on '
                                'Node {1} failed'.format(self._args['childid'],
                                                         nid))

    def __internalGet(self, n, s):
        if n and s:
            self.__getbySensorandNode(n, s)
        elif n:
            self.__getbyNode(n)
        return

    def get(self, node=False, sensor=False):
        self.__internalGet(node, sensor)
        return self._result if self._result else self._dbsession.query(Sensor).all()

    def openhab(self, node=False, sensor=False):
        self.__internalGet(node, sensor)
        return self._result.openhab if self._result else False

    def sensortype(self, node=False, sensor=False):
        self.__internalGet(node, sensor)
        return self._result.sensor_type if self._result else False

    def comment(self, node=False, sensor=False):
        self.__internalGet(node, sensor)
        return self._result.comment if self._result else False
