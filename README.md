pymygw
======

a mysensors to openhab gw based on https://github.com/wbcode/ham

### Requirements

- an arduino mysensors serial gateway connected via usb/serial on a linux host
- an openhab installation (not required for testing, but it would be usefull  :) )
- some sensors
- python pip installed


### Installation

```bash
    git clone https://github.com/thehawkes/pymygw.git
    cd pymygw
    pip install -r requirements.txt

```

### Configuration

change config.py
```python
OpenhabAPI = 'http://adugw.home:8080/rest/items'

SerialPort = '/dev/ttyACM0'

```

### Start
```bash
    cd <<installdirectory>>
    python pymygw.home
```

### TODO
- Webinterface to "glue" sensors to openhab


