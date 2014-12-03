pymygw
======

a [mysensors](http://www.mysensors.org/) gw based on https://github.com/wbcode/ham

- MQTT Support
- Openhab Rest Api Support

**MySensors Serial Protocol (1.4) support only**


[BLOG Post](http://www.the-hawkes.de/pymygw-a-simple-mysensors-gateway.html)



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

```

### Start
```bash
    cd <<installdirectory>>
    python pymygw.py
```

### Webinterface
**only available if the Openhab Rest Api is used as the publisher**
The gateway offers a simple Webinterface on Port 5000 to "glue" sensors to openhab items.

Edit config.py to change the port
```python
WebPort = 5000
```
