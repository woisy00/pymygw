pymygw
======

a [mysensors](http://www.mysensors.org/) gw based on https://github.com/wbcode/ham

- MQTT Support
- Openhab Rest Api Support

~~**MySensors Serial Protocol (1.4) support only**~~

Special thanks to

- [vincentdm](https://github.com/vincentdm)
- [meyerd](https://github.com/meyerd)

for adding v1.5 Serial API Support




*****




**Outdated** [BLOG Post](http://www.the-hawkes.de/pymygw-a-simple-mysensors-gateway.html)

### Requirements

- an arduino mysensors serial gateway connected via usb/serial on a linux host
- an openhab installation (not required for testing, but it would be usefull)
 - configured openhab items (atm only NumberItems are supported)
- some sensors
- python pip installed


### Installation

```bash
    git clone https://github.com/thehawkes/pymygw.git
    cd pymygw
    pip install -r requirements.txt

```

### Configuration

config.py
```python
# MQTT/Openhab
Publisher = 'MQTT'

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

'''
    Openhab config
'''
OpenhabAPI = 'http://adugw.home:8080/rest/items'
OpenhabAPIList = 'item'
OpenhabCacheTimeout = 300

```

### Start

```bash
    cd <<installdirectory>>
    python app.py
```

### Webinterface
**only available if the Openhab Rest Api is used as the publisher**

The gateway offers a simple Webinterface on Port 5000 to "glue" sensors to openhab items.

Edit config.py to change the port
```python
WebPort = 5000
```

