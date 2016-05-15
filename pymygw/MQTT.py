import paho.mqtt.client as mqtt
from logging import getLogger
from time import sleep

import config
import tools


class MQTT(object):
    def __init__(self):
        self._log = getLogger('pymygw')
        self.connected = False
        self._rc = {0: 'Connection successful',
                    1: 'Connection refused - incorrect protocol version',
                    2: 'Connection refused - invalid client identifier',
                    3: 'Connection refused - server unavailable',
                    4: 'Connection refused - bad username or password',
                    5: 'Connection refused - not authorised'}
        self.__client()

    def __client(self):
        self._PublishClient = mqtt.Client(client_id='pymygw-serialgw', protocol=config.MQTTProtocol)
        if config.MQTTTLS:
            if config.MQTTCert and config.MQTTKey:
                self._PublishClient.tls_set(config.MQTTCa,
                                            certfile=config.MQTTCert,
                                            keyfile=config.MQTTKey)
            else:
                self._PublishClient.tls_set(config.MQTTCa)
            # enable for testing only
            #self._PublishClient.tls_insecure_set(True)
            self.__connect(config.MQTTTLSPort)
        else:
            self.__connect(config.MQTTPort)

    def __setAuth(self):
        if config.MQTTUsername is not None and\
                config.MQTTPassword is not None:
            self._PublishClient.username_pw_set(config.MQTTUsername,
                                                password=config.MQTTPassword)

    def __connect(self, p):
        self._log.debug('MQTT connect started')
        self.__setAuth()

        self._PublishClient.on_connect = self.__on_connect
        self._PublishClient.on_disconnect = self.__on_disconnect
        self._PublishClient.on_publish = self.__on_publish
        self._PublishClient.on_log = self.__on_log

        self._PublishClient.connect(config.MQTTBroker, port=p)
        self._PublishClient.loop_start()
        # sleep to fix timing problem on rpi2
        sleep(1)
        if not self.connected:
            sleep(1)
            raise SystemExit('MQTT connection failed. Check Log')
        self._log.info('MQTT Client connected to Broker {0}'.format(config.MQTTBroker))


    '''
        MQTT Callbacks
    '''
    def __on_connect(self, client, userdata, flags, rc):
        self._log.debug('MQTT Connected with result code {0}, {1}'.format(rc, self._rc[rc]))
        if rc != 0:
            self._log.error('MQTT connection failed: {0}'.format(self._rc[rc]))
            self.connected = False
        self.connected = True

    def __on_disconnect(self, client, userdata, rc):
        if rc != 0:
            self._log.error('MQTT Unexpected disconnection')
        else:
            self._log.info('MQTT Client disconnected from Broker {0}'.format(config.MQTTBroker))
        self.connected = False

    def __on_publish(self, client, userdata, mid):
        pass

    def __on_log(self, client, userdata, level, msg):
        self._log.debug('MQTT Log: Level: {0}, Message: {1}'.format(level, msg))

    def __publish(self, topic, payload) :
        result, msgid = self._PublishClient.publish(topic, payload)

        self._log.debug('MQTT Returncode {0}, msgid {1}'.format(result, msgid))
        if result == 0:
            self._log.info('MQTT Publish successfully: {0} value: {1}'.format(topic, payload))
                                                                                    
        else:
            self._log.error('MQTT Publish failed: {0} value: {1}'.format(topic, payload))

    def publishSensorValue(self, msg, sensor):
        self._data = tools.checkKeys(msg, ('nodeid', 'childid', 'payload'))
        if self._data and self.connected:
            self._log.debug('Try to publish values to the MQTT Broker on {0}: {1}'.format(config.MQTTBroker,
                                                                                           msg))
            topic = "/" + config.MQTTTopic

            try:
                topic = topic.replace(
                    '%nodeid', self._data['nodeid']).replace(
                    '%childid', self._data['childid']).replace(
                    '%sensorid', self._data['childid']).replace(
                    '%type', msg['sensortype'])
					
                if not (sensor.name is None):
                    topic = topic.replace('%sensor_name', sensor.name)
                
                if not (sensor.node.name is None):
                    topic = topic.replace('%node_name', sensor.node.name)

                self._log.debug('Publishing to topic: {0}'.format(topic)) 
                self.__publish(topic, self._data['payload'])
            except Exception, e:
             self._log.error('MQTT Publish failed: Failed to create topic')
             self._log.error(e, exc_info=True)
             
    def publishInternalValue(self, msg, node):
        self._data = tools.checkKeys(msg, ('nodeid', 'childid', 'payload'))
        if self._data and self.connected:
            self._log.debug('Try to publish values to the MQTT Broker on {0}: {1}'.format(config.MQTTBroker,
                                                                                           msg))
            topic = "/" + config.InternalTopic

            try:
                topic = topic.replace(
                    '%nodeid', self._data['nodeid']).replace(
                    '%type', msg['sensortype'])
					
                if not (node.name is None):
                    topic = topic.replace('%node_name', node.name)

                self._log.debug('Publishing to topic: {0}'.format(topic)) 
                self.__publish(topic, self._data['payload'])
            except Exception, e:
             self._log.error('MQTT Publish failed: Failed to create topic')
             self._log.error(e, exc_info=True)
    
    def disconnect(self):
        self._PublishClient.disconnect()
