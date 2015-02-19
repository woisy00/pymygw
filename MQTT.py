import paho.mqtt.client as mqtt
import logging

import config


class MQTT(object):
    def __init__(self):
        self._log = logging.getLogger('pymygw')
        self.__client()

    def __client(self):
        self._PublishClient = mqtt.Client(client_id='pymygw-serialgw', protocol=config.MQTTProtocol)
        if config.MQTTTLS:
            self._PublishClient.tls_set(config.MQTTCa,
                                        certfile=config.MQTTCert,
                                        keyfile=config.MQTTKey)
            #enable for testing only
            #self._PublishClient.tls_insecure_set(True)
            self._PublishClient.connect(config.MQTTBroker,  port=config.MQTTTLSPort)
        else:
            self._PublishClient.connect(config.MQTTBroker, port=config.MQTTPort)
        self._PublishClient.loop_start()
        self._log.info('MQTT Client connected to Broker {0}'.format(config.MQTTBroker))

    def publish(self, node, child, value):
        returncode, msgid = self._PublishClient.publish('/{0}/{1}/{2}'.format(config.MQTTTopic, node, child), value)
        if returncode == 0:
            self._log.info('MQTT Publish successfully: /{0}/{1}/{2}, value: {3}'.format(config.MQTTTopic,
                                                                                        node,
                                                                                        child,
                                                                                        value))
        else:
            self._log.error('MQTT Publish failed: /{0}/{1}/{2}, value: {3}'.format(config.MQTTTopic,
                                                                                   node,
                                                                                   child,
                                                                                   value))

    def disconnect(self):
        self._PublishClient.disconnect()
        self._log.info('MQTT Client disconnected from Broker {0}'.format(config.MQTTBroker))
