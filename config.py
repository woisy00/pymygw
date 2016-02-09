'''
    Generic config
'''
DEBUG = True
LogFile = 'pymygw.log'
# MQTT or Openhab
Publisher = 'MQTT'

'''
    Arduino Serial config
'''
SerialPort = '/dev/ttyUSB0'
SerialBaud = 115200
SerialTimeOut = 1

'''
    MySensor generic config
'''
Seperator = ';'
UnitSystem = 'M'
EOL = '\n'

'''
    MQTT config


    TLS Attention
    !!!The broker dns name and the CN in the tls cert must be the same!!!
'''
MQTTBroker = '192.168.0.3'
#MQTTTLS = True
MQTTTLS = False
MQTTPort = 1883
MQTTTLSPort = 8883
#MQTTUsername = 'pymygw'
#MQTTPassword = 'pymygw'
MQTTUsername = None
MQTTPassword = None
# https://github.com/jpmens/mqttwarn/issues/95
MQTTProtocol = 3

'''
    MQTTTopic:
    
        Old behaviour is 'pymygw/%nodeid/%childid'
        Known substitions: 
            * %nodeid: replaced by the node ID assigned
            * %sensorid: replaced by the sensorID assigned by the node
            * %childdescription: Description as announced by the sensor.
'''
#MQTTTopic = 'pymygw/%nodeid/%childid'
MQTTTopic = 'pymygw/%childdescription'
MQTTCert = 'pymygw.crt'
MQTTKey = 'pymygw.key'
MQTTCa = 'ca.crt'

'''
    Web Config
    only available if the OpenhabAPI is used
'''
WebPort = 5000
WebDir = 'web'

'''
    Openhab config
'''
OpenhabAPI = 'http://192.168.0.3:8081/rest/items'
OpenhabAPIList = 'item'
OpenhabCacheTimeout = 300


'''
    Database
'''
Database = 'sqlite:///pymygw.db'

'''
    MySensor Serial Protocol Definition v1.5
    http://www.mysensors.org/build/serial_api

'''
MySensorStructureTemplate = {'nodeid': None,
                             'childid': None,
                             'messagetype': None,
                             'ack': 0,
                             'subtype': None,
                             'payload': None,
                             'sep': Seperator}

MySensorMessageType = {
    'PRESENTATION': {'id': 0, 'comment': 'Sent by a node when they present attached sensors. This is usually done in setup() at startup.'},
    'SET': {'id': 1, 'comment': 'This message is sent from or to a sensor when a sensor value should be updated'},
    'REQ': {'id': 2, 'comment': 'Requests a variable value (usually from an actuator destined for controller).'},
    'INTERNAL': {'id': 3, 'comment': 'This is a special internal message. See table below for the details'},
    'STREAM': {'id': 4, 'comment': 'Used for OTA firmware updates'},
}

MySensorPresentation = {
    'S_DOOR': {'id': 0, 'comment': 'Door and window sensors'},
    'S_MOTION': {'id': 1, 'comment': 'Motion sensors'},
    'S_SMOKE': {'id': 2, 'comment': 'Smoke sensor'},
    'S_LIGHT': {'id': 3, 'comment': 'Light Actuator (on/off)'},
    'S_BINARY': {'id': 3, 'comment': 'Binary Light or Relay (same as S_LIGHT)'},
    'S_DIMMER': {'id': 4, 'comment': 'Dimmable device of some kind'},
    'S_COVER': {'id': 5, 'comment': 'Window covers or shades'},
    'S_TEMP': {'id': 6, 'comment': 'Temperature sensor'},
    'S_HUM': {'id': 7, 'comment': 'Humidity sensor'},
    'S_BARO': {'id': 8, 'comment': 'Barometer sensor (Pressure)'},
    'S_WIND': {'id': 9, 'comment': 'Wind sensor'},
    'S_RAIN': {'id': 10, 'comment': 'Rain sensor'},
    'S_UV': {'id': 11, 'comment': 'UV sensor'},
    'S_WEIGHT': {'id': 12, 'comment': 'Weight sensor for scales etc.'},
    'S_POWER': {'id': 13, 'comment': 'Power measuring device, like power meters'},
    'S_HEATER': {'id': 14, 'comment': 'Heater device'},
    'S_DISTANCE': {'id': 15, 'comment': 'Distance sensor'},
    'S_LIGHT_LEVEL': {'id': 16, 'comment': 'Light sensor'},
    'S_ARDUINO_NODE': {'id': 17, 'comment': 'Arduino node device'},
    'S_ARDUINO_REPEATER_NODE': {'id': 18, 'comment': 'Arduino repeating node device'},
    'S_LOCK': {'id': 19, 'comment': 'Lock device'},
    'S_IR': {'id': 20, 'comment': 'Ir sender/receiver device'},
    'S_WATER': {'id': 21, 'comment': 'Water meter'},
    'S_AIR_QUALITY': {'id': 22, 'comment': 'Air quality sensor e.g. MQ-2'},
    'S_CUSTOM': {'id': 23, 'comment': 'Use this for custom sensors where no other fits.'},
    'S_DUST': {'id': 24, 'comment': 'Dust level sensor'},
    'S_SCENE_CONTROLLER': {'id': 25, 'comment': 'Scene controller device'},
    'S_RGB_LIGHT': {'id': 26, 'comment': 'RGB light. Send color component data using V_RGB. Also supports V_WATT'},
    'S_RGBW_LIGHT': {'id': 27, 'comment': 'RGB light with an additional White component. Send data using V_RGBW. Also supports V_WATT'},
    'S_COLOR_SENSOR': {'id': 28, 'comment': 'Color sensor, send color information using V_RGB'},
    'S_HVAC': {'id': 29, 'comment': 'Thermostat/HVAC device. V_HVAC_SETPOINT_HEAT, V_HVAC_SETPOINT_COLD, V_HVAC_FLOW_STATE, V_HVAC_FLOW_MODE, V_TEMP'},
    'S_MULTIMETER': {'id': 30, 'comment': 'Multimeter device, V_VOLTAGE, V_CURRENT, V_IMPEDANCE'},
    'S_SPRINKLER': {'id': 31, 'comment': 'Sprinkler, V_STATUS (turn on/off), V_TRIPPED (if fire detecting device)'},
    'S_WATER_LEAK': {'id': 32, 'comment': 'Water leak sensor, V_TRIPPED, V_ARMED'},
    'S_SOUND': {'id': 33, 'comment': 'Sound sensor, V_TRIPPED, V_ARMED, V_LEVEL (sound level in dB)'},
    'S_VIBRATION': {'id': 34, 'comment': 'Vibration sensor, V_TRIPPED, V_ARMED, V_LEVEL (vibration in Hz)'},
    'S_MOISTURE': {'id': 35, 'comment': 'Moisture sensor, V_TRIPPED, V_ARMED, V_LEVEL (water content or moisture in percentage?)'},
}

MySensorSetReq = {
    'V_TEMP': {'id': 0, 'comment': 'Temperature'},
    'V_HUM': {'id': 1, 'comment': 'Humidity'},
    'V_STATUS': {'id': 2, 'comment': 'S_LIGHT, S_DIMMER, S_SPRINKLER, S_HVAC, S_HEATER. Used for setting/reporting binary (on/off) status. 1=on, 0=off'},
    'V_LIGHT': {'id': 2, 'comment': 'Light status. 0=off 1=on'},
    'V_PERCENTAGE': {'id': 3, 'comment': 'S_DIMMER. Used for sending a percentage value 0-100 (%).'},
    'V_DIMMER': {'id': 3, 'comment': 'Dimmer value. 0-100%'},
    'V_PRESSURE': {'id': 4, 'comment': 'Atmospheric Pressure'},
    'V_FORECAST': {'id': 5, 'comment': 'Whether forecast. One of stable, sunny, cloudy, unstable, thunderstorm or unknown'},
    'V_RAIN': {'id': 6, 'comment': 'Amount of rain'},
    'V_RAINRATE': {'id': 7, 'comment': 'Rate of rain'},
    'V_WIND': {'id': 8, 'comment': 'Windspeed'},
    'V_GUST': {'id': 9, 'comment': 'Gust'},
    'V_DIRECTION': {'id': 10, 'comment': 'Wind direction'},
    'V_UV': {'id': 11, 'comment': 'UV light level'},
    'V_WEIGHT': {'id': 12, 'comment': 'Weight (for scales etc)'},
    'V_DISTANCE': {'id': 13, 'comment': 'Distance'},
    'V_IMPEDANCE': {'id': 14, 'comment': 'Impedance value'},
    'V_ARMED': {'id': 15, 'comment': 'Armed status of a security sensor. 1=Armed, 0=Bypassed'},
    'V_TRIPPED': {'id': 16, 'comment': 'Tripped status of a security sensor. 1=Tripped, 0=Untripped'},
    'V_WATT': {'id': 17, 'comment': 'Watt value for power meters'},
    'V_KWH': {'id': 18, 'comment': 'Accumulated number of KWH for a power meter'},
    'V_SCENE_ON': {'id': 19, 'comment': 'Turn on a scene'},
    'V_SCENE_OFF': {'id': 20, 'comment': 'Turn of a scene'},
    'V_HEATER': {'id': 21, 'comment': 'Mode of header. One of Off, HeatOn, CoolOn, or AutoChangeOver'},
    'V_HEATER_SW': {'id': 22, 'comment': 'Heater switch power. 1=On, 0=Off'},
    'V_LIGHT_LEVEL': {'id': 23, 'comment': 'Light level. 0-100%'},
    'V_VAR1': {'id': 24, 'comment': 'Custom value'},
    'V_VAR2': {'id': 25, 'comment': 'Custom value'},
    'V_VAR3': {'id': 26, 'comment': 'Custom value'},
    'V_VAR4': {'id': 27, 'comment': 'Custom value'},
    'V_VAR5': {'id': 28, 'comment': 'Custom value'},
    'V_UP': {'id': 29, 'comment': 'Window covering. Up.'},
    'V_DOWN': {'id': 30, 'comment': 'Window covering. Down.'},
    'V_STOP': {'id': 31, 'comment': 'Window covering. Stop.'},
    'V_IR_SEND': {'id': 32, 'comment': 'Send out an IR-command'},
    'V_IR_RECEIVE': {'id': 33, 'comment': 'This message contains a received IR-command'},
    'V_FLOW': {'id': 34, 'comment': 'Flow of water (in meter)'},
    'V_VOLUME': {'id': 35, 'comment': 'Water volume'},
    'V_LOCK_STATUS': {'id': 36, 'comment': 'Set or get lock status. 1=Locked, 0=Unlocked'},
    'V_DUST_LEVEL': {'id': 37, 'comment': 'Dust level'},
    'V_VOLTAGE': {'id': 38, 'comment': 'Voltage level'},
    'V_CURRENT': {'id': 39, 'comment': 'Current level'},
    'V_RGB': {'id': 40, 'comment': 'S_RGB_LIGHT, S_COLOR_SENSOR. Used for sending color information for multi color LED lighting or color sensors. Sent as ASCII hex: RRGGBB (RR=red, GG=green, BB=blue component)'},
    'V_RGBW': {'id': 41, 'comment': 'S_RGBW_LIGHT Used for sending color information to multi color LED lighting. Sent as ASCII hex: RRGGBBWW (WW=white component)'},
    'V_ID': {'id': 42, 'comment': 'S_TEMP Used for sending in sensors hardware ids (i.e. OneWire DS1820b).'},
    'V_UNIT_PREFIX': {'id': 43, 'comment': 'S_DUST, S_AIR_QUALITY Allows sensors to send in a string representing the unit prefix to be displayed in GUI, not parsed by controller! E.g. cm, m, km, inch. Can be used for S_DISTANCE or gas concentration'},
    'V_HVAC_SETPOINT_COOL': {'id': 44, 'comment': 'S_HVAC. HVAC cool setpoint (Integer between 0-100)'},
    'V_HVAC_SETPOINT_HEAT': {'id': 45, 'comment': 'S_HEATER, S_HVAC. HVAC/Heater setpoint (Integer between 0-100)'},
    'V_HVAC_FLOW_MODE': {'id': 46, 'comment': 'S_HVAC. Flow mode for HVAC ("Auto", "ContinuousOn", "PeriodicOn")'},
}

MySensorInternal = {
    'I_BATTERY_LEVEL': {'id': 0, 'comment': 'Use this to report the battery level (in percent 0-100).'},
    'I_TIME': {'id': 1, 'comment': 'Sensors can request the current time from the Controller using this message. The time will be reported as the seconds since 1970'},
    'I_VERSION': {'id': 2, 'comment': 'Sensors report their library version at startup using this message type'},
    'I_ID_REQUEST': {'id': 3, 'comment': 'Use this to request a unique node id from the controller.'},
    'I_ID_RESPONSE': {'id': 4, 'comment': 'Id response back to sensor. Payload contains sensor id.'},
    'I_INCLUSION_MODE': {'id': 5, 'comment': 'Start/stop inclusion mode of the Controller (1=start, 0=stop).'},
    'I_CONFIG': {'id': 6, 'comment': 'Config request from node. Reply with (M)etric or (I)mperal back to sensor.'},
    'I_FIND_PARENT': {'id': 7, 'comment': 'When a sensor starts up, it broadcast a search request to all neighbor nodes. They reply with a I_FIND_PARENT_RESPONSE.'},
    'I_FIND_PARENT_RESPONSE': {'id': 8, 'comment': 'Reply message type to I_FIND_PARENT request.'},
    'I_LOG_MESSAGE': {'id': 9, 'comment': 'Sent by the gateway to the Controller to trace-log a message'},
    'I_CHILDREN': {'id': 10, 'comment': 'A message that can be used to transfer child sensors (from EEPROM routing table) of a repeating node.'},
    'I_SKETCH_NAME': {'id': 11, 'comment': 'Optional sketch name that can be used to identify sensor in the Controller GUI'},
    'I_SKETCH_VERSION': {'id': 12, 'comment': 'Optional sketch version that can be reported to keep track of the version of sensor in the Controller GUI.'},
    'I_REBOOT': {'id': 13, 'comment': 'Used by OTA firmware updates. Request for node to reboot.'},
    'I_GATEWAY_READY': {'id': 14, 'comment': 'Send by gateway to controller when startup is complete.'},
    'I_REQUEST_SIGNING': {'id': 15, 'comment': 'Signing request'},
    'I_GET_NONCE': {'id': 16, 'comment': 'Request a nonce'},
    'I_GET_NONCE_RESPONSE': {'id': 17, 'comment': 'Reply with a nonce'},
}
