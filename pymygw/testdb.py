
from sqlalchemy import create_engine, Column, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.exc import NoResultFound

import Database
import sys


Base = declarative_base()
db = Database.Database()

#if "-f" in sys.argv:
    #engine = create_engine('sqlite:///pymygw.db')
    #Base.metadata.create_all(engine)
    #Base.metadata.bind = engine
    #dbsession = scoped_session(sessionmaker(bind=engine))
    #n1 = Database.Sensor(node_id = 1, sensor_id = 1, openhab = 'blubber')
    #n2 = Database.Sensor(node_id = 1, sensor_id = 2, sensor_type = 'sensorblubber')
    #n3 = Database.Sensor(node_id = 2, sensor_id = 1, comment = 'comment blubber')
    #n4 = Database.Sensor(node_id = 3, sensor_id = 1, openhab = 'ophabblubber', comment='bin da', sensor_type='hum')
    #dbsession.add(n1)
    #dbsession.add(n2)
    #dbsession.add(n3)
    #dbsession.add(n4)
    #dbsession.commit()
    #dbsession.close()
    #sys.exit(0)


print 'known node 1 sensor 0: {0}'.format(db.isknown(node=1))
print 'unknown node 1 sensor 4: {0}'.format(db.isknown(node=1, sensor=4))
print 'unknown node 4 sensor 0: {0}'.format(db.isknown(node=4, sensor=0))

#print 'unknown sensor 1_1: {0}'.format(db.isknown(node='1_1'))
#print 'malformed sensor 11: {0}'.format(db.isknown(node='11'))
#print '-'*30
#print 'get single 1_2: {0}'.format(db.get(node='1_2'))
#print 'get all: {0}'.format(db.get())
#print '-'*30
#print 'get openhab 1_2: {0}'.format(db.openhab(node=1, sensor=1))
#print 'get sensortyp 2_1: {0}'.format(db.openhab(node=2, sensor=1))
#print 'get sensortyp 1_2: {0}'.format(db.sensortype(node=1, sensor=2))
#print 'get sensortyp 3_1: {0}'.format(db.comment(node=3, sensor=1))
#print '-'*30
#print 'add new sensor node: {0}'.format(db.add())

#print 'updating node 1 sensor 0: {0}'.format(db.add(node=1, sensor=0, sensortype='Node1', comment="with commit"))
#newid = db.add()
#print 'adding node {1} sensor 2: {0}'.format(db.add(node=newid, sensor=2, sensortype='Node4'), newid)
#print 'adding node {1} sensor 0: {0}'.format(db.add(node=newid, sensor=1, sensortype='Node423'), newid)
#print 'updating sensor 1 sensor 1: {0}'.format(db.add(node=1, sensor=1, sensortype='bluber'))
