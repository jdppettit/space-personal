from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Server(db.Model):
    __tablename__ = "server"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    disk_size = db.Column(db.Integer)
    disk_path = db.Column(db.String(100))
    vcpu = db.Column(db.Integer)
    ram = db.Column(db.Integer)
    state = db.Column(db.Integer)
    image = db.Column(db.String(100))
    inconsistent = db.Column(db.Integer)
    mac_address = db.Column(db.String(20))

    def __init__(self, name, disk_size, disk_path, ram, state, image, vcpu):
        self.name = name
        self.disk_size = disk_size
        self.disk_path = disk_path
        self.ram = ram
        self.state = state
        self.image = image
        self.vcpu = vcpu

class Image(db.Model):
    __tablename__ = "image"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    path = db.Column(db.String(100))
    size = db.Column(db.Integer)

    def __init__(self, name, path, size):
        self.name = name
        self.path = path
        self.size = size

class Event(db.Model):
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    type = db.Column(db.Integer)
    server_id = db.Column(db.Integer)

    def __init__(self, type, server_id, date):
        self.type = type
        self.server_id = server_id
        self.date = date

class Log(db.Model):
    __tablename__ = "log"
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    message = db.Column(db.String(100))
    level = db.Column(db.Integer)

    def __init__(self, date, message, level):
        self.date = date
        self.message = message
        self.level = level

class IPAddress(db.Model):
    __tablename__ = "ipaddress"

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(20))
    netmask = db.Column(db.Integer)
    status = db.Column(db.Integer)
    server_id = db.Column(db.Integer)
    gateway = db.Column(db.Integer)

    def __init__(self, ip, netmask, status, server_id, gateway):
        self.ip = ip
        self.netmask = netmask
        self.status = status
        self.server_id = server_id
        self.gateway = gateway

class Host(db.Model):
    __tablename__ = "host"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    ram = db.Column(db.Integer)

    def __init__(self, name, ram):
        self.name = name
        self.ram = ram
