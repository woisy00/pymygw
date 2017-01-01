from sqlalchemy import Table, MetaData, Column, Integer, Float, String, Boolean, UniqueConstraint, ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, reconstructor
from sqlalchemy import orm
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import mapper
from logging import getLogger
from sqlalchemy.sql import select
import traceback
from migrate import *

log = getLogger('pymygw')
                           
class Node(object):
    
    # v2: calculate battery fill level with min/max voltage setting
    # and publish via mqtt
    #min_voltage = Column(Integer, default=0)
    #max_voltage = Column(Integer, default=0)

    def __repr__(self):
        return json.dumps({'Node': self.node_id,
                           'Name': self.name,
                           'Sketch Name': self.sketch_name,
                           'Sketch Version': self.sketch_version,
                           'Status': self.status,
                           'API Version': self.api_version,
                           'Battery': self.battery,
                           'Battery Level': self.battery_level})
            

class Sensor(object):
    
    def __repr__(self):
        return json.dumps({'Node': self.node_id,
                           'Name': self.name,
                           'Sensor': self.sensor_id,
                           'Type': self.sensor_type,
                           'Comment': self.comment,
                           'Description': self.description,
                           'Last Seen': self.last_seen,
                           'Last Value': self.last_value})


class FirmwareType(object):
    
    def __repr__(self):
        return json.dumps({'Name': self.name})
                           
class Firmware(object):

    def __repr__(self):
        return json.dumps({'Type': self.type_id,
                           'Version': self.version,
                           'Blocks': self.blocks,
                           'CRC': self.crc,
                           'data': self.data})
    @orm.reconstructor
    def init_on_load(self):
        self.__parse()
        
    def getBlock(self, block):
        return self.__fwdata[block]
    
    def parse(self, type, version, data):
        self.type_id = type.id
        self.version = version
        self.data = data
        self.__parse()
        
    def __parse(self):
        fwdata = []
        start = 0
        end = 0
        pos = 0
        
        for l in self.data.split("\n"):
            line = l.strip()
            if len(line) > 0:
                while line[0:1] != ":":
                    line = line[1:]
                reclen = int(line[1:3], 16)
                offset = int(line[3:7], 16)
                rectype = int(line[7:9], 16)
                data = line[9:9 + 2 * reclen]
                chksum = int(line[9 + (2 * reclen):9 + (2 * reclen) + 2], 16)
                if rectype == 0:
                    if start == 0 and end == 0:
                        if offset % 128 > 0:
                            raise Error("error loading hex file - offset can't be devided by 128")
                        start = offset
                        end = offset

                    if offset < end:
                        raise Error("error loading hex file - offset lower than end")
                    while offset > end:
                        fwdata.append(255)
                        pos = pos + 1
                        end = end + 1
                        
                    for i in range(0, reclen):
                        fwdata.append(int(data[i * 2:(i * 2) + 2], 16))
                        pos = pos + 1
                    end += reclen
        pad = end % 128
        for i in range(0, 128 - pad):
            fwdata.append(255)
            pos = pos + 1
            end = end + 1
        self.blocks = (end - start) / 16
        crc = 0xFFFF
        for i in range(0, self.blocks * 16):
            crc = self.__crc(crc, fwdata[i])

        self.crc = crc
        self.__fwdata = fwdata
        
    def __crc(self, old, data):
        crc = old ^ data
        for bit in range(0, 8):
            if (crc&0x0001) == 0x0001:
                crc = ((crc >> 1) ^ 0xA001)
            else:
                crc = crc >> 1
        return crc
        

def getSchema(engine):
    if Schema.instance is None:
        Schema.instance = Schema(engine)
        Schema.instance.upgrade()
    
    return Schema.instance

        
class Schema(object):

    instance = None
            
    def __init__(self, engine):
        self._engine = engine
        self._metadata = MetaData()
        self._metadata.bind = engine
        self._schema_version = None
        self._version = 2
        
        
    def upgrade(self):
        self.loadVersion()
        log.warning('Upgrading Database schema from version {0} to version {1}'.format(self._schema_version, self._version))
        
        for version in range(1, self._version + 1):
            log.warning('Upgrading schema version to {0}'.format(version))
            schema_fun = 'upgrade_{0}_Schema'.format(version)
            ddl_fun = 'upgrade_{0}_DDL'.format(version)
            if self._schema_version < version:
                if hasattr(self.__class__, ddl_fun) and callable(getattr(self.__class__, ddl_fun)):
                    log.warning('Executing ddl function: {0}'.format(ddl_fun))
                    getattr(self, ddl_fun)()
                self._setSchemaVersion(version)
                
            if hasattr(self.__class__, schema_fun) and callable(getattr(self.__class__, schema_fun)):
                log.warning('Executing schema function: {0}'.format(schema_fun))
                getattr(self, schema_fun)()

        
        
        mapper(FirmwareType, Table('firmware_type', self._metadata))
        
        mapper(Firmware, Table('firmware', self._metadata), properties={
            'type' : relationship(FirmwareType)
        })
        
        mapper(Node, Table('node', self._metadata), properties={
            'firmware' : relationship(Firmware)
        })
        
        mapper(Sensor, Table('sensor', self._metadata), properties={
            'node' : relationship(Node)
        })
        
    def getVersion(self):
        return self._version
        
    def loadVersion(self):
        if self._schema_version is None:
            self.schem_version_table = Table('schema_version', self._metadata,
                Column('version', Integer)
                )
            self.schem_version_table.create(checkfirst=True)
        
            with self._engine.connect() as conn:
                s = select([self.schem_version_table])                
                result = conn.execute(s)
                row = result.fetchone()
                if row is None:
                    i = self.schem_version_table.insert().values(version=0)
                    conn.execute(i)
                    self._schema_version = 0
                else:
                    self._schema_version = row['version']
        
        if self._schema_version is None:
            self._schema_version = 0
    
    def _setSchemaVersion(self, version):
        log.warning('Upgrading schema version to {0}'.format(version))
        with self._engine.connect() as conn:
            u = self.schem_version_table.update().values(version=version)
            conn.execute(u)
            self._schema_version = version
    
    def upgrade_1_Schema(self):
        firmware_type_table = Table('firmware_type', self._metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(20), default=None, unique=True)
            )
        firmware_type_table.create(checkfirst=True)
        
        firmware_table = Table('firmware', self._metadata,
            Column('id', Integer, primary_key=True),
            Column('type_id', Integer, ForeignKey('firmware_type.id'), nullable=False),
            Column('version', String(20), default=None),
            Column('data', String(4000))
            )
        firmware_table.create(checkfirst=True)
        
        node_table = Table('node', self._metadata,
            Column('id', Integer, primary_key=True),
            Column('node_id', Integer, nullable=False),
            Column('name', String(60), default=None),
            Column('status', String(20), default=None),
            Column('sketch_name', String(60), default=None),
            Column('sketch_version', String(60), default=None),
            Column('api_version', String(20), default=None),
            Column('battery', Integer, default=0),
            Column('battery_level', Float, default=0),
            Column('requestReboot', Boolean, default=False),
            Column('firmware_id', Integer, ForeignKey('firmware.id'))
            )
        node_table.create(checkfirst=True)
        
        sensor_table = Table('sensor', self._metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(29), default=None),
            Column('node_id', Integer, ForeignKey('node.node_id'), nullable=False),
            Column('sensor_id', Integer, default=0),
            Column('sensor_type', String(20), default=None),
            Column('comment', String(255)),
            Column('description', String(255)),
            Column('last_seen', Integer, default=0),
            Column('last_value', String(20), default=0),
            UniqueConstraint('node_id', 'sensor_id')
            )
        sensor_table.create(checkfirst=True)

    def upgrade_2_Schema(self):
        Table('node', self._metadata, 
            Column('min_voltage', Integer, default=0),
            Column('max_voltage', Integer, default=0),
            extend_existing=True)
        
    def upgrade_2_DDL(self):
        node = Table('node', self._metadata)
        min_voltage = Column('min_voltage', Integer, default=0)            
        min_voltage.create(node)
        
        max_voltage = Column('max_voltage', Integer, default=0)
        max_voltage.create(node)        
