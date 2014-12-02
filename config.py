'''
    Generic config
'''
DEBUG = True
LogFile = 'pymygw.log'
Publish = 'mqtt'

'''
    Web Config
'''
WebPort = 5000
WebDir = 'web'

'''
    Openhab config
'''
OpenhabAPI = 'http://adugw.home:8080/rest/items'
OpenhabAPIList = 'item'
OpenhabCacheTimeout = 300

'''
    MQTT config
'''
MQTTBroker = 'adugw.home'
MQTTPort = 1883
#https://github.com/jpmens/mqttwarn/issues/95
MQTTProtocol = 3
MQTTTopic = 'pymygw'

'''
    Arduino Serial config
'''
SerialPort = '/dev/ttyACM0'
SerialBaud = 115200
SerialTimeOut = 5


'''
    MySensor generic config
'''
Seperator = ';'
MaxNodes = 254
MaxChilds = 254
EOL = '\n'
'''
    units are metric
'''
UnitSystem = 'M'


'''
    Database
'''
Database = '.pymygw.db'
DatabaseTable = 'sensors'
DatabaseTableCreate = 'CREATE TABLE IF NOT EXISTS {0} (id TEXT UNIQUE, typ TEXT, openhab TEXT UNIQUE)'.format(DatabaseTable)


'''
    MySensor Serial Protocol Definition v1.4 (Beta)
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
    'S_ARDUINO_RELAY': {'id': 18, 'comment': 'Arduino repeating node device'},
    'S_LOCK': {'id': 19, 'comment': 'Lock device'},
    'S_IR': {'id': 20, 'comment': 'Ir sender/receiver device'},
    'S_WATER': {'id': 21, 'comment': 'Water meter'},
    'S_AIR_QUALITY': {'id': 22, 'comment': 'Air quality sensor e.g. MQ-2'},
    'S_CUSTOM': {'id': 23, 'comment': 'Use this for custom sensors where no other fits.'},
    'S_DUST': {'id': 24, 'comment': 'Dust level sensor'},
    'S_SCENE_CONTROLLER': {'id': 25, 'comment': 'Scene controller device'},
}

MySensorSetReq = {
    'V_TEMP': {'id': 0, 'comment': 'Temperature'},
    'V_HUM': {'id': 1, 'comment': 'Humidity'},
    'V_LIGHT': {'id': 2, 'comment': 'Light status. 0=off 1=on'},
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
}
