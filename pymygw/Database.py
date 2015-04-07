from sqlalchemy import create_engine, Column, Integer, Float, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.exc import NoResultFound
import time
import json
from logging import getLogger

import config
Base = declarative_base()

class Sensor(Base):
    __tablename__ = 'sensor'
    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, nullable=False)
    sensor_id = Column(Integer, default=0)
    sensor_type = Column(String(20), default=None)
    openhab = Column(String(90), unique=True, nullable=True)
    comment = Column(String(255))
    battery = Column(Integer, default=0)
    battery_level = Column(Float, default=0)
    api_version = Column(String(20), default=None)
    sketch_name = Column(String(60), default=None)
    sketch_version = Column(String(60), default=None)
    last_seen = Column(Integer, default=0)

    __table_args__ = (UniqueConstraint('node_id', 'sensor_id'),)


    def __str__(self):
        return json.dumps({'Node': self.node_id,
                           'Sensor': self.sensor_id,
                           'Type': self.sensor_type,
                           'Openhab': self.openhab,
                           'Comment': self.comment,
                           'Battery': self.battery,
                           'Battery Level': self.battery_level,
                           'API Version': self.api_version,
                           'Sketch Version': self.sketch_version,
                           'Sketch Name': self.sketch_name,
                           'Last Seen': self.last_seen})


class Database():
    def __init__(self):
        self._log = getLogger('pymygw')
        self._engine = create_engine(config.Database)
        Base.metadata.create_all(self._engine)
        Base.metadata.bind = self._engine
        self._dbsession = scoped_session(sessionmaker(bind=self._engine))

    def __getsingle(self, n, s):
        self._node = n
        self._sensor = s
        self._result = None
        try:
            self._result = self._dbsession.query(Sensor)\
                                          .filter(Sensor.node_id == self._node,
                                                  Sensor.sensor_id == self._sensor)\
                                          .one()
        except NoResultFound:
            self._log.debug('No DB entry found for Node: {0} Sensor; {1}'.format(n, s))

    def __commit(self):
        try:
            self._dbsession.commit()
            self._log.debug('Commit successfull: {0}'.format(self._result))
            return True
        except Exception, e:
            self._log.error('Commit failed for {0} \n\
                             Exception: {1}'.format(self._result, e))
            self._dbsession.rollback()
            return False

    def __update(self, timestamp=False):
        if timestamp:
            self._result.last_seen = time.time()
            if self.__commit():
                return True
            return False

        else:
            '''
                updates the db entrie if needed
            '''
            self._changed = False
            if 'sensortype' in self._addargs and \
                    self._addargs['sensortype'] != self._result.sensor_type:
                self._log.error('SensorType mismatch for {0} \n\
                                 Reported Type: {3}'.format(self._result,
                                                            sensortype))

                return False

            if 'openhab' in self._addargs and \
                    self._addargs['openhab'] != self._result.openhab:
                self._log.debug('OpenhabDB entry update for {0} \n\
                                 New Openhab: {3}'.format(self._result,
                                                          openhab))
                self._changed = True
                self._result.openhab = openhab

            if 'comment' in self._addargs and \
                    self._addargs['comment'] != self._result.comment:
                self._changed = True
                self._result.comment = comment

            if 'battery' in self._addargs and \
                    self._addargs['battery'] != self._result.battery:
                self._changed = True
                self._result.battery = self._addargs['battery']

            if 'battery_level' in self._addargs and \
                    self._addargs['battery_level'] != self._result.battery_level:
                self._changed = True
                self._result.battery_level = self._addargs['battery_level']

            if 'api_version' in self._addargs and \
                    self._addargs['api_version'] != self._result.api_version:
                self._changed = True
                self._result.api_version = self._addargs['api_version']

            if 'sketch_version' in self._addargs and \
                    self._addargs['sketch_version'] != self._result.sketch_version:
                self._changed = True
                self._result.sketch_version = self._addargs['sketch_version']

            if 'sketch_name' in self._addargs and \
                    self._addargs['sketch_name'] != self._result.sketch_name:
                self._changed = True
                self._result.sketch_name = self._addargs['sketch_name']


            if self._changed:
                if self.__commit():
                    self._log.debug('Update for {0} '
                                    'finished successfully'.format(self._result))
                    return True
                else:
                    self._log.error('Updated failed for {0}'.format(self._result))
                    return False

            self._log.debug('Nothing to update for {0}'.format(self._result))
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
                         sensor_id=sensor,
                         last_seen=time.time())
        self._dbsession.add(newnode)
        if self.__commit():
            self._log.debug('New node added to DB: {0}'.format(newnode))
            return newid
        else:
            self._log.error('Adding node failed: {0}'.format(newode))
            return False



    def add(self, node=False, sensor=0, sensortype=None, **kwargs):
        self._addargs = kwargs
        if not node:
            return False
        self.__getsingle(node, sensor)
        if self._result:
            '''
                Node + Sensor is known
                update entry
            '''
            self.__update()
        else:
            '''
                Node + Sensor is unknown
                create new DB entrie
            '''
            if self.isknown(node=node):
                '''
                    node is known, but new sensor
                '''
                nid = self._node
            else:
                '''
                    Node is unknown (old Sensor)
                '''
                nid = node
            newsensor = Sensor(node_id=nid,
                                sensor_id=sensor,
                                sensor_type=sensortype,
                                last_seen=time.time())
            self._dbsession.add(newsensor)
            self._log.info('adding new sensor')
            if self.__commit():
                self._log.info('Sensor {0} added on'
                               'Node {1}'.format(sensor,
                                                 nid))
                return True
            else:
                self._log.error('Adding Sensor {0} on '
                                'Node {1} failed'.format(sensor,
                                                         nid))
                return False
        return False

    def get(self, node=False, sensor=0):
        self.__getsingle(node, sensor)
        return self._result if self._result else self._dbsession.query(Sensor).all()

    def isknown(self, node=False, sensor=0):
        self.__getsingle(node, sensor)
        if self._result:
            self.__update(timestamp=True)
        return bool(self._result)

    def openhab(self, node=False, sensor=0):
        self.__getsingle(node, sensor)
        return self._result.openhab if self._result else False

    def sensortype(self, node=False, sensor=0):
        self.__getsingle(node, sensor)
        return self._result.sensor_type if self._result else False

    def comment(self, node=False, sensor=0):
        self.__getsingle(node, sensor)
        return self._result.comment if self._result else False
