from pymygw.Database import Database, Node, Sensor
import os
from random import randint

myfile = 'pymygw.db'
if os.path.isfile(myfile):
    os.remove(myfile)

db = Database()

for i in range(10):
    newNode = Node(node_id=i)
    db._dbsession.add(newNode)
    db._dbsession.commit()
    #print 'Current Nodes: {0}'.format(db._dbsession.query(Node).all())

    oldnode = db._dbsession.query(Node).filter(Node.node_id == i).one()
    for s in range(2):
        newsensor = Sensor(sensor_id=s, node_id=oldnode.node_id, comment='{0} sensor'.format(s))
        db._dbsession.add(newsensor)
        db._dbsession.commit()
    print 'Sensors on {0}'.format(oldnode.node_id)
    for s in oldnode.sensors:
        print s
    print '-'*20


print '#'*50
for i in range(3):
    rand = randint(0,9)
    print 'ID {0}'.format(rand)
    q = db._dbsession.query(Node).filter(Node.node_id == rand).one()
    print 'Node: ', q.node_id
    print 'Sketch Name: ', q.sketch_name
    print 'Sketch Version: ', q.sketch_version
    print 'API: ', q.api_version
    print 'Battery: ', q.battery
    print 'Battery Level: ', q.battery_level
    for s in q.sensors:
        print s
    print '-'*30


print '+'*50
for i in range(3):
    rand = randint(0,9)
    print 'ID {0}'.format(rand)
    q = db._dbsession.query(Sensor).filter(Sensor.node_id == rand).all()
    for e in q:
        print e
    
