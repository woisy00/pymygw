from sqlalchemy import create_engine, Column, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.exc import NoResultFound

Base = declarative_base()

class Sensor(Base):
    __tablename__ = 'sensor'
    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, nullable=False)
    sensor_id = Column(Integer, default=0)
    sensor_type = Column(Integer, default=None)
    openhab = Column(String(90), unique=True, nullable=True)
    comment = Column(String(255))
    last_seen = Column(Integer, default=0)

    __table_args__ = (UniqueConstraint('node_id', 'sensor_id'),)


class Database():
    def __init__(self):
        self._engine = create_engine('sqlite:///pymygw.db')
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
            pass

    def add(self, node=False, sensor=0, sensortype=None, openhab=None, comment=None):
        '''
            if node is not set -> new sensor node
            - get new id, add(block) it, return it
        '''
        if not node:
            lastid = self._dbsession.query(Sensor.node_id).order_by(Sensor.node_id.desc()).first()
            if lastid is None:
                newid = 1
            else:
                newid = lastid[0] + 1
            newnode = Sensor(node_id=newid)
            self._dbsession.add(newnode)
            self._dbsession.commit()
            return newid

        else:
            self.__getsingle(node, sensor)
            if self._result:
                '''
                    node with sensor is known
                '''
                self._result.sensor = sensor
                self._changed = False
                if sensortype and sensortype != self._result.sensor_type:
                    #self._changed = True
                    #self._result.sensor_type = sensortype
                    return False
                if openhab and openhab != self._result.openhab:
                    self._changed = True
                    self._result.openhab = openhab
                if comment and comment != self._result.comment:
                    self._changed = True
                    self._result.comment = comment
                if self._changed:
                    self._dbsession.commit()
                    return "Updated with commit"
                return "Nothing to update"
            else:
                if self.isknown(node=node):
                    '''
                        node is known, but new sensor
                    '''
                    newsensor = Sensor(node_id=node,
                                       sensor_id=sensor,
                                       sensor_type=sensortype,
                                       openhab=openhab,
                                       comment=comment)
                    self._dbsession.add(newsensor)
                    self._dbsession.commit()
                    return "Sensor added"
            return False

    def get(self, node=False, sensor=0):
        self.__getsingle(node, sensor)
        return self._result if self._result else self._dbsession.query(Sensor).all()

    def isknown(self, node=False, sensor=0):
        self.__getsingle(node, sensor)
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
