import paho.mqtt.client as mqtt
import sys
from logging import getLogger

import config
import tools


class MQTT(object):
    def __init__(self):
        self._log = getLogger('pymygw')
        self.__client()

    def __setAuth(self):
        if config.MQTTUsername is not None and\
                config.MQTTPassword is not None:
            self._PublishClient.username_pw_set(config.MQTTUsername,
                                                password=config.MQTTPassword)

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

    def __connect(self, p):
        try:
            self.__setAuth()
            self._PublishClient.connect(config.MQTTBroker, port=p)
        except Exception, e:
            self._log.error('MQTT Client connection to Broker {0}, Port {1} failed. {2}'.format(config.MQTTBroker,
                                                                                                p,
                                                                                                e))
            sys.exit(10)
        self._PublishClient.loop_start()
        self._log.info('MQTT Client connected to Broker {0}'.format(config.MQTTBroker))

    def publish(self, msg):
        self._log.debug('Try to publish values to the MQTT Brocker on {0}: {1}'.format(config.MQTTBroker,
                                                                                       msg))
        self._data = tools.checkKeys(msg, ('nodeid', 'childid', 'payload'))
        if self._data:
            returncode, msgid = self._PublishClient.publish('/{0}/{1}/{2}'.format(config.MQTTTopic,\
                                                                                  self._data['nodeid'],\
                                                                                  self._data['childid']),\
                                                                                  self._data['payload'])
            if returncode == 0:
                self._log.info('MQTT Publish successfully: /{0}/{1}/{2}, value: {3}'.format(config.MQTTTopic,
                                                                                            self._data['nodeid'],
                                                                                            self._data['childid'],
                                                                                            self._data['payload']))
            else:
                self._log.error('MQTT Publish failed: /{0}/{1}/{2}, value: {3}'.format(config.MQTTTopic,
                                                                                       self._data['nodeid'],
                                                                                       self._data['childid'],
                                                                                       self._data['payload']))

    def disconnect(self):
        self._PublishClient.disconnect()
        self._log.info('MQTT Client disconnected from Broker {0}'.format(config.MQTTBroker))
