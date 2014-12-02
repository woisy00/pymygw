import paho.mqtt.client as mqtt
import logging

import config


class MQTT(object):
    def __init__(self):
        self._log = logging.getLogger('pymygw')
        self.__client()

    def __client(self):
        self._PublishClient = mqtt.Client(client_id='pymygw-serialgw', protocol=config.MQTTProtocol)
        self._PublishClient.connect(config.MQTTBroker, port=config.MQTTPort)
        self._PublishClient.loop_start()
        self._log.info('MQTT Client connected to Broker {0}'.format(config.MQTTBroker))

    def publish(self, node, child, value):
        self._PublishClient.publish('/{0}/{1}/{2}'.format(config.MQTTTopic, node, child), value)
        self._log.debug('MQTT Publish: /{0}/{1}/{2}, value: {3}'.format(config.MQTTTopic,
                                                                        node,
                                                                        child,
                                                                        value))

    def disconnect(self):
        self._PublishClient.disconnect()
        self._log.info('MQTT Client disconnected from Broker {0}'.format(config.MQTTBroker))
