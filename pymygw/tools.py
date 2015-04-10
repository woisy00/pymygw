from logging import getLogger

def checkKeys(msg, keys):
    data = {}
    log = getLogger('pymygw')
    if not all (k in msg for k in keys):
            log.error('missing key in message {0}\n'
                      'keys: {1}'.format(msg, keys))
            return False
    for k in keys:
        data[k] = msg[k]
    return data


