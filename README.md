pymygw
======

a [mysensors](http://www.mysensors.org/) to openhab gw based on https://github.com/wbcode/ham 

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
OpenhabAPI = 'http://adugw.home:8080/rest/items'

SerialPort = '/dev/ttyACM0'

```

### Start
```bash
    cd <<installdirectory>>
    python pymygw.py
```

### Webinterface
The gateway offers a simple Webinterface on Port 5000 to "glue" sensors to openhab items.

Edit config.py to change the port
```python
WebPort = 5000
```
