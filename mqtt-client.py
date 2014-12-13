import paho.mqtt.client as mqtt
from subprocess import Popen
import re

MQTTSub = '/openhab/radio/'
RCSWITCH = '/opt/rcswitch-pi/send'
SWITCHES = {}

REGX_HCODE = re.compile(r'[10]{5}')
REGX_CID = re.compile(r'[0-9]{1}')

class InvalidHcode(Exception):
    pass

class InvalidCID(Exception):
    pass

class InvalidAction(Exception):
    pass


class Switch(object):
    def __init__(self, name, hcode, cid):
        if not REGX_HCODE.match(hcode):
            raise InvalidHcode('Invalid House Code {0}'.format(hcode))
        if not REGX_CID.match(cid):
            raise InvalidCID('Invalid Client ID {0}'.format(cid))
        self._name = name
        self._housecode = hcode
        self._clientid = cid
        self._cmd = None
        self._status = None

    def action(self, acode):
        self._actioncode = int(acode)
        if self._actioncode == 0:
            self.switch()
        elif self._actioncode == 1:
            self.switch()
        else:
            raise InvalidAction('Invalid Action {0}'.format(self._actioncode))

    def switch(self):
        if self._actioncode != self._status:
            self._status = self._actioncode
            self._cmd = [str(RCSWITCH),
                         str(self._housecode),
                         str(self._clientid),
                         str(self._actioncode)]
            self._execute()

    def name(self):
        return self._name

    def _execute(self):
        print 'execute {0}'.format(self._cmd)
        p = Popen(self._cmd)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe('{0}#'.format(MQTTSub))


def on_message(client, userdata, msg):
    switch, housecode, node = msg.topic.strip(MQTTSub).split('/')
    state = msg.payload
    if switch in SWITCHES:
        print 'found {0} in SWITCHES'.format(switch)
        try:
            SWITCHES[switch].action(state)
        except Exception, e:
            print e
    else:
        print 'new node {0}'.format(switch)
        try:
            o = Switch(switch, housecode, node)
            SWITCHES[switch] = o
            o.action(state)
        except Exception, e:
            print e
    print 'switch {0}, housecode {1}, node {2}, state {3}'.format(switch, housecode, node, state)


client = mqtt.Client(protocol=3)
client.on_connect = on_connect
client.on_message = on_message

client.connect("adugw.home", 1883, 60)

client.loop_forever()
