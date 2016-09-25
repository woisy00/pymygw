'''
    Generic config
'''
DEBUG = False
LogFile = 'pymygw.log'
FirmwareDir = '/opt/pymygw/firmwares'

'''
    Arduino Serial config
'''
SerialPort = '/dev/mysensors'
SerialBaud = 115200
SerialTimeOut = 1

'''
    MySensor generic config
'''
UnitSystem = 'M'
EOL = '\n'

'''
    MQTT config


    TLS Attention
    !!!The broker dns name and the CN in the tls cert must be the same!!!
'''
MQTTBroker = '127.0.0.1' #192.168.0.3'
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
MQTTTopicPrefix = 'mysensors'
#MQTTTopic = 'pymygw/%childdescription'
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
    Database
'''
Database = 'sqlite:///pymygw.db'


MySensorPresentation = {
    'S_DOOR': {'name': 'S_DOOR', 'id': 0, 'comment': 'Door and window sensors'},
    'S_MOTION': {'name': 'S_MOTION', 'id': 1, 'comment': 'Motion sensors'},
    'S_SMOKE': {'name': 'S_SMOKE', 'id': 2, 'comment': 'Smoke sensor'},
    'S_LIGHT': {'name': 'S_LIGHT', 'id': 3, 'comment': 'Light Actuator (on/off)'},
    'S_BINARY': {'name': 'S_BINARY', 'id': 3, 'comment': 'Binary device (on/off), Alias for S_LIGHT'},
    'S_DIMMER': {'name': 'S_DIMMER', 'id': 4, 'comment': 'Dimmable device of some kind'},
    'S_COVER': {'name': 'S_COVER', 'id': 5, 'comment': 'Window covers or shades'},
    'S_TEMP': {'name': 'S_TEMP', 'id': 6, 'comment': 'Temperature sensor'},
    'S_HUM': {'name': 'S_HUM', 'id': 7, 'comment': 'Humidity sensor'},
    'S_BARO': {'name': 'S_BARO', 'id': 8, 'comment': 'Barometer sensor (Pressure)'},
    'S_WIND': {'name': 'S_WIND', 'id': 9, 'comment': 'Wind sensor'},
    'S_RAIN': {'name': 'S_RAIN', 'id': 10, 'comment': 'Rain sensor'},
    'S_UV': {'name': 'S_UV', 'id': 11, 'comment': 'UV sensor'},
    'S_WEIGHT': {'name': 'S_WEIGHT', 'id': 12, 'comment': 'Weight sensor for scales etc.'},
    'S_POWER': {'name': 'S_POWER', 'id': 13, 'comment': 'Power measuring device, like power meters'},
    'S_HEATER': {'name': 'S_HEATER', 'id': 14, 'comment': 'Heater device'},
    'S_DISTANCE': {'name': 'S_DISTANCE', 'id': 15, 'comment': 'Distance sensor'},
    'S_LIGHT_LEVEL': {'name': 'S_LIGHT_LEVEL', 'id': 16, 'comment': 'Light sensor'},
    'S_ARDUINO_NODE': {'name': 'S_ARDUINO_NODE', 'id': 17, 'comment': 'Arduino node device'},
    'S_ARDUINO_REPEATER_NODE': {'name': 'S_ARDUINO_REPEATER_NODE', 'id': 18, 'comment': 'Arduino repeating node device'},
    'S_LOCK': {'name': 'S_LOCK', 'id': 19, 'comment': 'Lock device'},
    'S_IR': {'name': 'S_IR', 'id': 20, 'comment': 'Ir sender/receiver device'},
    'S_WATER': {'name': 'S_WATER', 'id': 21, 'comment': 'Water meter'},
    'S_AIR_QUALITY': {'name': 'S_AIR_QUALITY', 'id': 22, 'comment': 'Air quality sensor e.g. MQ-2'},
    'S_CUSTOM': {'name': 'S_CUSTOM', 'id': 23, 'comment': 'Use this for custom sensors where no other fits.'},
    'S_DUST': {'name': 'S_DUST', 'id': 24, 'comment': 'Dust level sensor'},
    'S_SCENE_CONTROLLER': {'name': 'S_SCENE_CONTROLLER', 'id': 25, 'comment': 'Scene controller device'},
    'S_RGB_LIGHT': {'name': 'S_RGB_LIGHT', 'id': 26, 'comment': 'RGB light'},
    'S_RGBW_LIGHT': {'name': 'S_RGBW_LIGHT', 'id': 27, 'comment': 'RGBW light (with separate white component)'},
    'S_COLOR_SENSOR': {'name': 'S_COLOR_SENSOR', 'id': 28, 'comment': 'Color sensor'},
    'S_HVAC': {'name': 'S_HVAC', 'id': 29, 'comment': 'Thermostat/HVAC device'},
    'S_MULTIMETER': {'name': 'S_MULTIMETER', 'id': 30, 'comment': 'Multimeter device'},
    'S_SPRINKLER': {'name': 'S_SPRINKLER', 'id': 31, 'comment': 'Sprinkler device'},
    'S_WATER_LEAK': {'name': 'S_WATER_LEAK', 'id': 32, 'comment': 'Water leak sensor'},
    'S_SOUND': {'name': 'S_SOUND', 'id': 33, 'comment': 'Sound sensor'},
    'S_VIBRATION': {'name': 'S_VIBRATION', 'id': 34, 'comment': 'Vibration sensor'},
    'S_MOISTURE': {'name': 'S_MOISTURE', 'id': 35, 'comment': 'Moisture sensor'},
    'S_INFO': {'name': 'S_INFO', 'id': 36, 'comment': 'LCD text device'},
    'S_GAS': {'name': 'S_GAS', 'id': 37, 'comment': 'Gas meter'},
    'S_GPS': {'name': 'S_GPS', 'id': 38, 'comment': 'GPS Sensor'},
    'S_WATER_QUALITY': {'name': 'S_WATER_QUALITY', 'id': 39, 'comment': 'Water quality sensor'},
}

MySensorSetReq = {
    'V_TEMP': {'name': 'V_TEMP', 'id': 0, 'comment': 'Temperature'},
    'V_HUM': {'name': 'V_HUM', 'id': 1, 'comment': 'Humidity'},
    'V_STATUS': {'name': 'V_STATUS', 'id': 2, 'comment': 'Binary status. 0=off 1=on'},
    'V_LIGHT': {'name': 'V_LIGHT', 'id': 2, 'comment': 'Deprecated. Alias for V_STATUS. Light status. 0=off 1=on'},
    'V_PERCENTAGE': {'name': 'V_PERCENTAGE', 'id': 3, 'comment': 'Percentage value. 0-100 (%)'},
    'V_DIMMER': {'name': 'V_DIMMER', 'id': 3, 'comment': 'Deprecated. Alias for V_PERCENTAGE. Dimmer value. 0-100 (%)'},
    'V_PRESSURE': {'name': 'V_PRESSURE', 'id': 4, 'comment': 'Atmospheric Pressure'},
    'V_FORECAST': {'name': 'V_FORECAST', 'id': 5, 'comment': 'Whether forecast. One of "stable", "sunny", "cloudy", "unstable", "thunderstorm" or "unknown"'},
    'V_RAIN': {'name': 'V_RAIN', 'id': 6, 'comment': 'Amount of rain'},
    'V_RAINRATE': {'name': 'V_RAINRATE', 'id': 7, 'comment': 'Rate of rain'},
    'V_WIND': {'name': 'V_WIND', 'id': 8, 'comment': 'Windspeed'},
    'V_GUST': {'name': 'V_GUST', 'id': 9, 'comment': 'Gust'},
    'V_DIRECTION': {'name': 'V_DIRECTION', 'id': 10, 'comment': 'Wind direction'},
    'V_UV': {'name': 'V_UV', 'id': 11, 'comment': 'UV light level'},
    'V_WEIGHT': {'name': 'V_WEIGHT', 'id': 12, 'comment': 'Weight (for scales etc)'},
    'V_DISTANCE': {'name': 'V_DISTANCE', 'id': 13, 'comment': 'Distance'},
    'V_IMPEDANCE': {'name': 'V_IMPEDANCE', 'id': 14, 'comment': 'Impedance value'},
    'V_ARMED': {'name': 'V_ARMED', 'id': 15, 'comment': 'Armed status of a security sensor. 1=Armed, 0=Bypassed'},
    'V_TRIPPED': {'name': 'V_TRIPPED', 'id': 16, 'comment': 'Tripped status of a security sensor. 1=Tripped, 0=Untripped'},
    'V_WATT': {'name': 'V_WATT', 'id': 17, 'comment': 'Watt value for power meters'},
    'V_KWH': {'name': 'V_KWH', 'id': 18, 'comment': 'Accumulated number of KWH for a power meter'},
    'V_SCENE_ON': {'name': 'V_SCENE_ON', 'id': 19, 'comment': 'Turn on a scene'},
    'V_SCENE_OFF': {'name': 'V_SCENE_OFF', 'id': 20, 'comment': 'Turn of a scene'},
    'V_HVAC_FLOW_STATE': {'name': 'V_HVAC_FLOW_STATE', 'id': 21, 'comment': 'Mode of header. One of "Off", "HeatOn", "CoolOn", or "AutoChangeOver"'},
    'V_HVAC_SPEED': {'name': 'V_HVAC_SPEED', 'id': 22, 'comment': 'HVAC/Heater fan speed ("Min", "Normal", "Max", "Auto")'},
    'V_LIGHT_LEVEL': {'name': 'V_LIGHT_LEVEL', 'id': 23, 'comment': 'Uncalibrated light level. 0-100%. Use V_LEVEL for light level in lux.'},
    'V_VAR1': {'name': 'V_VAR1', 'id': 24, 'comment': 'Custom value'},
    'V_VAR2': {'name': 'V_VAR2', 'id': 25, 'comment': 'Custom value'},
    'V_VAR3': {'name': 'V_VAR3', 'id': 26, 'comment': 'Custom value'},
    'V_VAR4': {'name': 'V_VAR4', 'id': 27, 'comment': 'Custom value'},
    'V_VAR5': {'name': 'V_VAR5', 'id': 28, 'comment': 'Custom value'},
    'V_UP': {'name': 'V_UP', 'id': 29, 'comment': 'Window covering. Up.'},
    'V_DOWN': {'name': 'V_DOWN', 'id': 30, 'comment': 'Window covering. Down.'},
    'V_STOP': {'name': 'V_STOP', 'id': 31, 'comment': 'Window covering. Stop.'},
    'V_IR_SEND': {'name': 'V_IR_SEND', 'id': 32, 'comment': 'Send out an IR-command'},
    'V_IR_RECEIVE': {'name': 'V_IR_RECEIVE', 'id': 33, 'comment': 'This message contains a received IR-command'},
    'V_FLOW': {'name': 'V_FLOW', 'id': 34, 'comment': 'Flow of water (in meter)'},
    'V_VOLUME': {'name': 'V_VOLUME', 'id': 35, 'comment': 'Water volume'},
    'V_LOCK_STATUS': {'name': 'V_LOCK_STATUS', 'id': 36, 'comment': 'Set or get lock status. 1=Locked, 0=Unlocked'},
    'V_LEVEL': {'name': 'V_LEVEL', 'id': 37, 'comment': 'Used for sending level-value'},
    'V_VOLTAGE': {'name': 'V_VOLTAGE', 'id': 38, 'comment': 'Voltage level'},
    'V_CURRENT': {'name': 'V_CURRENT', 'id': 39, 'comment': 'Current level'},
    'V_RGB': {'name': 'V_RGB', 'id': 40, 'comment': 'RGB value transmitted as ASCII hex string (I.e "ff0000" for red)'},
    'V_RGBW': {'name': 'V_RGBW', 'id': 41, 'comment': 'RGBW value transmitted as ASCII hex string (I.e "ff0000ff" for red + full white)'},
    'V_ID': {'name': 'V_ID', 'id': 42, 'comment': 'Optional unique sensor id (e.g. OneWire DS1820b ids)'},
    'V_UNIT_PREFIX': {'name': 'V_UNIT_PREFIX', 'id': 43, 'comment': 'Allows sensors to send in a string representing the unit prefix to be displayed in GUI. This is not parsed by controller! E.g. cm, m, km, inch.'},
    'V_HVAC_SETPOINT_COOL': {'name': 'V_HVAC_SETPOINT_COOL', 'id': 44, 'comment': 'HVAC cold setpoint'},
    'V_HVAC_SETPOINT_HEAT': {'name': 'V_HVAC_SETPOINT_HEAT', 'id': 45, 'comment': 'HVAC/Heater setpoint'},
    'V_HVAC_FLOW_MODE': {'name': 'V_HVAC_FLOW_MODE', 'id': 46, 'comment': 'Flow mode for HVAC ("Auto", "ContinuousOn", "PeriodicOn")'},
    'V_TEXT': {'name': 'V_TEXT', 'id': 47, 'comment': 'Text message to display on LCD or controller device'},
    'V_CUSTOM': {'name': 'V_CUSTOM', 'id': 48, 'comment': 'Custom messages used for controller/inter node specific commands, preferably using S_CUSTOM device type.'},
    'V_POSITION': {'name': 'V_POSITION', 'id': 49, 'comment': 'GPS position and altitude. Payload: latitude;longitude;altitude(m). E.g. "55.722526;13.017972;18"'},
    'V_IR_RECORD': {'name': 'V_IR_RECORD', 'id': 50, 'comment': 'Record IR codes S_IR for playback'},
    'V_PH': {'name': 'V_PH', 'id': 51, 'comment': 'Water PH'},
    'V_ORP': {'name': 'V_ORP', 'id': 52, 'comment': 'Water ORP : redox potential in mV'},
    'V_EC': {'name': 'V_EC', 'id': 53, 'comment': 'Water electric conductivity uS/cm (microSiemens/cm)'},
    'V_VAR': {'name': 'V_VAR', 'id': 54, 'comment': 'Reactive power: volt-ampere reactive (var)'},
    'V_VA': {'name': 'V_VA', 'id': 55, 'comment': 'Apparent power: volt-ampere (VA)'},
    'V_POWER_FACTOR': {'name': 'V_POWER_FACTOR', 'id': 56, 'comment': 'Ratio of real power to apparent power: floating point value in the range [-1,..,1]'}
}

MySensorInternal = {
    'I_BATTERY_LEVEL': {'name': 'I_BATTERY_LEVEL', 'id': 0, 'comment': 'Use this to report the battery level (in percent 0-100).'},
    'I_TIME': {'name': 'I_TIME', 'id': 1, 'comment': 'Sensors can request the current time from the Controller using this message. The time will be reported as the seconds since 1970'},
    'I_VERSION': {'name': 'I_VERSION', 'id': 2, 'comment': 'Used to request gateway version from controller.'},
    'I_ID_REQUEST': {'name': 'I_ID_REQUEST', 'id': 3, 'comment': 'Use this to request a unique node id from the controller.'},
    'I_ID_RESPONSE': {'name': 'I_ID_RESPONSE', 'id': 4, 'comment': 'Id response back to node. Payload contains node id.'},
    'I_INCLUSION_MODE': {'name': 'I_INCLUSION_MODE', 'id': 5, 'comment': 'Start/stop inclusion mode of the Controller (1=start, 0=stop).'},
    'I_CONFIG': {'name': 'I_CONFIG', 'id': 6, 'comment': 'Config request from node. Reply with (M)etric or (I)mperal back to sensor.'},
    'I_FIND_PARENT': {'name': 'I_FIND_PARENT', 'id': 7, 'comment': 'When a sensor starts up, it broadcast a search request to all neighbor nodes. They reply with a I_FIND_PARENT_RESPONSE.'},
    'I_FIND_PARENT_RESPONSE': {'name': 'I_FIND_PARENT_RESPONSE', 'id': 8, 'comment': 'Reply message type to I_FIND_PARENT request.'},
    'I_LOG_MESSAGE': {'name': 'I_LOG_MESSAGE', 'id': 9, 'comment': 'Sent by the gateway to the Controller to trace-log a message'},
    'I_CHILDREN': {'name': 'I_CHILDREN', 'id': 10, 'comment': 'A message that can be used to transfer child sensors (from EEPROM routing table) of a repeating node.'},
    'I_SKETCH_NAME': {'name': 'I_SKETCH_NAME', 'id': 11, 'comment': 'Optional sketch name that can be used to identify sensor in the Controller GUI'},
    'I_SKETCH_VERSION': {'name': 'I_SKETCH_VERSION', 'id': 12, 'comment': 'Optional sketch version that can be reported to keep track of the version of sensor in the Controller GUI.'},
    'I_REBOOT': {'name': 'I_REBOOT', 'id': 13, 'comment': 'Used by OTA firmware updates. Request for node to reboot.'},
    'I_GATEWAY_READY': {'name': 'I_GATEWAY_READY', 'id': 14, 'comment': 'Send by gateway to controller when startup is complete.'},
    'I_REQUEST_SIGNING': {'name': 'I_REQUEST_SIGNING', 'id': 15, 'comment': 'Used between sensors when initialting signing.'},
    'I_GET_NONCE': {'name': 'I_GET_NONCE', 'id': 16, 'comment': 'Used between sensors when requesting nonce.'},
    'I_GET_NONCE_RESPONSE': {'name': 'I_GET_NONCE_RESPONSE', 'id': 17, 'comment': 'Used between sensors for nonce response.'},
    'I_HEARTBEAT': {'name': 'I_HEARTBEAT', 'id': 18, 'comment': 'Heartbeat request'},
    'I_PRESENTATION': {'name': 'I_PRESENTATION', 'id': 19, 'comment': 'Presentation message'},
    'I_DISCOVER': {'name': 'I_DISCOVER', 'id': 20, 'comment': 'Discover request'},
    'I_DISCOVER_RESPONSE': {'name': 'I_DISCOVER_RESPONSE', 'id': 21, 'comment': 'Discover response'},
    'I_HEARTBEAT_RESPONSE': {'name': 'I_HEARTBEAT_RESPONSE', 'id': 22, 'comment': 'Heartbeat response'},
    'I_LOCKED': {'name': 'I_LOCKED', 'id': 23, 'comment': 'Node is locked (reason in string-payload)'},
    'I_PING': {'name': 'I_PING', 'id': 24, 'comment': 'Ping sent to node, payload incremental hop counter'},
    'I_PONG': {'name': 'I_PONG', 'id': 25, 'comment': 'In return to ping, sent back to sender, payload incremental hop counter'},
    'I_REGISTRATION_REQUEST': {'name': 'I_REGISTRATION_REQUEST', 'id': 26, 'comment': 'Register request to GW'},
    'I_REGISTRATION_RESPONSE': {'name': 'I_REGISTRATION_RESPONSE', 'id': 27, 'comment': 'Register response from GW'},
    'I_DEBUG': {'name': 'I_DEBUG', 'id': 28, 'comment': 'Debug message'},
}

MySensorStream = {
    'ST_FIRMWARE_CONFIG_REQUEST': {'name': 'ST_FIRMWARE_CONFIG_REQUEST', 'id': 0, 'comment': 'Request firmware config.'},
    'ST_FIRMWARE_CONFIG_RESPONSE': {'name': 'ST_FIRMWARE_CONFIG_RESPONSE', 'id': 1, 'comment': 'Response to firmware config request.'},
    'ST_FIRMWARE_REQUEST': {'name': 'ST_FIRMWARE_REQUEST', 'id': 2, 'comment': 'Request firmware block.'},
    'ST_FIRMWARE_RESPONSE': {'name': 'ST_FIRMWARE_RESPONSE', 'id': 3, 'comment': 'Response with firmware block.'},
    'ST_SOUND': {'name': 'ST_SOUND', 'id': 4, 'comment': 'Play sound?'},
    'ST_IMAGE': {'name': 'ST_IMAGE', 'id': 5, 'comment': 'Image from camera?'},
}


MySensorMessageType = {
    'PRESENTATION': {'name': 'PRESENTATION', 'id': 0, 'comment': 'Sent by a node when they present attached sensors. This is usually done in setup() at startup.', 'subTypes': MySensorPresentation},
    'SET': {'name': 'SET', 'id': 1, 'comment': 'This message is sent from or to a sensor when a sensor value should be updated', 'subTypes': MySensorSetReq},
    'REQ': {'name': 'REQ', 'id': 2, 'comment': 'Requests a variable value (usually from an actuator destined for controller).', 'subTypes': MySensorSetReq},
    'INTERNAL': {'name': 'INTERNAL', 'id': 3, 'comment': 'This is a special internal message. See table below for the details', 'subTypes': MySensorInternal},
    'STREAM': {'name': 'STREAM', 'id': 4, 'comment': 'Used for OTA firmware updates', 'subTypes': MySensorStream},
}
