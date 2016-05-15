from flask import Flask, render_template, g, request, redirect, url_for
from datetime import datetime
from logging import getLogger

import config
import Database
import os

from operator import attrgetter

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
log = getLogger('pymygw')

@app.before_request
def before_request():
    g.db = Database.Database2()


@app.template_filter('timestamp2date')
def timestamp2date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

@app.route('/')
def index():
    return render_template('index.html',
                           data=sorted(g.db.loadSensors(), key=attrgetter('node_id', 'sensor_id')))


@app.route('/nodes', methods=['GET', 'POST'])
def nodes():
    if request.method == 'POST':
        typeName=request.form['name']
        fwt = g.db.getFirmwareType(typeName)
        if fwt is None:
            fwt = g.db.addFirmwareType(typeName)
        
        g.db.addFirmware(fwt, request.form['version'], data)


    return render_template('nodes.html',
                           nodes=g.db.loadNodes(),
                           firmwares=g.db.loadFirmwares())

@app.route('/node/<nodeId>', methods=['GET', 'POST'])
def node(nodeId):
    node = g.db.getNode(nodeId)
    
    if request.method == 'POST':
        anythingChanged = False
        firmwareId = request.form['firmware']
        nodeName = request.form['node_name']
        
        if firmwareId == '':
            firmwareId = None
        if node.firmware_id != firmwareId:
            log.info('Updating Node {0} to firmwareid {1}'.format(nodeId, firmwareId))
            node.firmware_id = firmwareId
            node.requestReboot = True
            anythingChanged = True
            
            
        if node.name != nodeName:
            node.name = nodeName
            anythingChanged = True
        
        if anythingChanged:
            g.db.commit()

    return render_template('nodedetail.html',
                           node=node,
                           firmwares=sorted(g.db.loadFirmwares(), key=attrgetter('type_id', 'version')))

@app.route('/delete/node/<nodeId>')
def delete_node(nodeId):
    g.db.deleteNode(nodeId)
    return redirect(url_for('nodes'))
    
@app.route('/reboot/node/<nodeId>')
def reboot_node(nodeId):
    node = g.db.getNode(nodeId)
    node.requestReboot = True
    g.db.commit()
    return redirect(url_for('nodes'))
    
@app.route('/firmware', methods=['GET', 'POST'])
def firmware():
    if request.method == 'POST':
        f = request.files['firmware']
        data=f.read()
        typeName=request.form['name']
        fwt = g.db.getFirmwareType(typeName)
        if fwt is None:
            fwt = g.db.addFirmwareType(typeName)
        
        g.db.addFirmware(fwt, request.form['version'], data)
        fw_file_name = os.path.join(config.FirmwareDir, 
                "{0}_{1}.hex".format(fwt.name, request.form['version']))
        with open(fw_file_name, 'w') as fw_file:
            fw_file.write(data)
    firmwares = g.db.loadFirmwares()
    
    sorted(firmwares, key=attrgetter('type_id', 'version'))

    return render_template('firmware.html',
                            data=sorted(firmwares, key=attrgetter('type_id', 'version')))