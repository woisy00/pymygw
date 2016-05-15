pymygw
======

a [mysensors](http://www.mysensors.org/) gw based on https://github.com/thehawkes/pymygw

- MQTT Support
- OTA Firmware updates

*****

### Requirements

- an arduino mysensors serial gateway connected via usb/serial on a linux host
- some sensors
- python pip installed


### Installation

```bash
    git clone https://github.com/woisy00/pymygw.git
    cd pymygw
    pip install -r requirements.txt

```

### Configuration

config.py
```python

'''
    Arduino Serial config
'''
SerialPort = '/dev/ttyACM0'


'''
    MQTT config


    TLS Attention
    !!!The broker dns name and the CN in the tls cert must be the same!!!
'''
MQTTBroker = 'mqtt.home'
MQTTTLS = True
MQTTPort = 1883
MQTTTLSPort = 8883
MQTTUsername = 'pymygw'
MQTTPassword = 'pymygw'
# https://github.com/jpmens/mqttwarn/issues/95
MQTTProtocol = 3
MQTTTopic = 'pymygw'
MQTTCert = 'pymygw.crt'
MQTTKey = 'pymygw.key'
MQTTCa = 'ca.crt'

'''
    Web Config
    only available if the OpenhabAPI is used
'''
WebPort = 5000
WebDir = 'web'

```

### Start

```bash
    cd <<installdirectory>>
    python app.py
```

### Webinterface
The gateway offers a simple Webinterface on Port 5000.

Edit config.py to change the port
```python
WebPort = 5000
```

