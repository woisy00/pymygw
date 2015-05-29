from pymygw.Database import Database2, Node, Sensor
import os
from random import randint

myfile = 'pymygw.db'
if os.path.isfile(myfile):
    os.remove(myfile)

db = Database2()
nodecount = 4
maxsensor = 4

print '+'*50
print 'creating {0} new Nodes'.format(nodecount)
print '+'*50
for i in range(nodecount):
    newid = db.newNodeID()
    print 'Node {0} created'.format(newid)
    print db.get(node=newid)
    sensorcount = randint(1, maxsensor)
    print 'Creating {0} Sensors on Node {1}'.format(sensorcount, newid)
    for s in range(sensorcount):
        newsensor = Sensor(sensor_id=s, node_id=newid, comment='{0} sensor'.format(s))
        db._dbsession.add(newsensor)
        db._dbsession.commit()
    for s in db.get(node=newid).sensors:
        print s
    print '-'*20


#print '#'*50
#print 'query rand node'
#print '#'*50
#for i in range(2):
#    rand = randint(0,3)
#    print 'ID {0}'.format(rand)
#    q = db._dbsession.query(Node).filter(Node.node_id == rand).one()
#    print 'Node: ', q.node_id
#    print 'Sketch Name: ', q.sketch_name
#    print 'Sketch Version: ', q.sketch_version
#    print 'API: ', q.api_version
#    print 'Battery: ', q.battery
#    print 'Battery Level: ', q.battery_level
#    for s in q.sensors:
#        print s
#    print '-'*30
#
#
#print '+'*50
#print 'Query Sensor for rand Node'
#print '+'*50
#for i in range(2):
#    rand = randint(0,3)
#    print 'ID {0}'.format(rand)
#    q = db._dbsession.query(Sensor).filter(Sensor.node_id == rand).all()
#    for e in q:
#        print e
#
#print '+'*50
#print 'Adding new Node, testing NewNodeID'
#print '+'*50
#newid = db.newNodeID()
#print 'Requested new Node ID: {0}'.format(newid)
#print 'Query newly created Node: {0}'.format(newid)
#q = db._dbsession.query(Node).filter(Node.node_id == newid).one()
#print 'Node: ', q.node_id
#print 'Sketch Name: ', q.sketch_name
#print 'Sketch Version: ', q.sketch_version
#print 'API: ', q.api_version
#print 'Battery: ', q.battery
#print 'Battery Level: ', q.battery_level
#
#
