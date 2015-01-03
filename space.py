from flask import *
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.basicauth import BasicAuth

from config import *
from domfunctions import *

import libvirt
import subprocess
import datetime

app = Flask(__name__)

connectionString = "mysql+mysqlconnector://%s:%s@%s:3306/%s" % (username, password, hostname, database)
app.config['SQLALCHEMY_DATABASE_URI'] = connectionString
db = SQLAlchemy(app)

app.config['BASIC_AUTH_USERNAME'] = ba_username
app.config['BASIC_AUTH_PASSWORD'] = ba_password
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)

class Server(db.Model):
    __tablename__ = "server"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    disk_size = db.Column(db.Integer)
    disk_path = db.Column(db.String(100))
    ram = db.Column(db.Integer)
    state = db.Column(db.Integer)
    image = db.Column(db.String(100))

    def __init__(self, name, disk_size, disk_path, ram, state, image):
        self.name = name
        self.disk_size = disk_size
        self.disk_path = disk_path
        self.ram = ram
        self.state = state
        self.image = image

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

'''
Event Types
1 = Create
2 = Destroy
3 = Boot
4 = Shutdown
'''

db.create_all()
db.session.commit()

def get_images():
    images = Image.query.all()
    return images

@app.route('/ip', methods=['POST','GET'])
def ips():
    if request.method == "GET":
        ips = IPAddress.query.all()
        return render_template("ips.html", ips=ips)
    else:
        address = request.form['address']
        netmask = request.form['netmask']
        new_ip = IPAddress(address, netmask, 0, 0, "0")
        message = "Added new IP %s/%s" % (str(address), str(netmask))
        logm = Log(datetime.datetime.now(), message, 1)
        db.session.add(new_ip)
        db.session.add(logm)
        db.session.commit()
        return redirect('/ip')

@app.route('/')
def index():
    servers = Server.query.filter(Server.state != 3).all()
    images = get_images()
    log = Log.query.all()
    return render_template("index.html", servers = servers, images=images, log=log)

@app.route('/create', methods=['POST'])
def create():
    name = request.form['name']
    ram = request.form['ram']
    disk_size = request.form['disk_size']
    image = request.form['image']
    image_obj = Image.query.filter_by(id=image).first()
    new_vm = Server(name, disk_size, "", ram, 1, image_obj.name)
    db.session.add(new_vm)
    db.session.commit()
    db.session.refresh(new_vm)
    disk_path = "/var/disks/vm%s.img" % str(new_vm.id)
    new_vm.disk_path = disk_path
    new_event = Event(1, new_vm.id, datetime.datetime.now())
    boot_event = Event(3, new_vm.id, datetime.datetime.now())
    db.session.add(new_event)
    db.session.add(boot_event)
    db.session.commit()
    create_vm(new_vm.id, ram, disk_size, image_obj.path)
    return redirect('/')

@app.route('/destroy/<vmid>')
def destroy(vmid):
    vm = Server.query.filter_by(id=vmid).first()
    vm.state = 3
    new_event = Event(2, vm.id, datetime.datetime.now())
    db.session.add(new_event)
    db.session.commit()
    delete_vm(vm.id, vm.disk_path)
    return redirect('/')


@app.route('/shutdown/<vmid>')
def shutdown(vmid):
    vm = Server.query.filter_by(id=vmid).first()
    vm.state = 0
    new_event = Event(4, vm.id, datetime.datetime.now())
    db.session.add(new_event)
    db.session.commit()
    shutdown_vm(vm.id)
    return redirect('/')

@app.route('/start/<vmid>')
def start(vmid):
    vm = Server.query.filter_by(id=vmid).first()
    vm.state = 1
    new_event = Event(3, vm.id, datetime.datetime.now())
    db.session.add(new_event)
    db.session.commit()
    start_vm(vm.id)
    return redirect('/')

@app.route('/viewall')
def view_all():
    domains = Server.query.filter_by(state=3).all()
    return render_template("view_deleted.html", domains=domains)

@app.route('/edit/<vmid>', methods=['POST','GET'])
def edit(vmid):
    if request.method == "GET":
        server = Server.query.filter_by(id=vmid).first()
        events = Event.query.filter_by(server_id=server.id).all()
        return render_template("edit.html", server=server, events=events)
    else:
        vm = Server.query.filter_by(id=vmid).first()
        vm.name = request.form['name']
        vm.ram = request.form['ram']
        vm.disk_size = request.form['disk_size']
        vm.image = request.form['image']
        vm.state = request.form['state']
        db.session.commit()
        return redirect('/edit/%s' % str(vmid))

@app.route('/images', methods=['POST','GET'])
def images():
    if request.method == "GET":
        images = Image.query.all()
        return render_template("images.html", images=images)
    else:
        new_image = Image(request.form['name'], request.form['path'], request.form['size'])
        message = "Created new image %s of size %s at %s" % (str(new_image.name), str(new_image.size), str(new_image.path))
        logm = Log(str(datetime.datetime.now()), message, 1)
        db.session.add(logm)
        db.session.add(new_image)
        db.session.commit()
        return redirect('/images')

@app.route('/image/edit/<imageid>', methods=['POST','GET'])
def edit_image(imageid):
    if request.method == "GET":
        image = Image.query.filter_by(id=imageid).first()
        return render_template("edit_image.html", image=image)
    else:
        image = Image.query.filter_by(id=imageid).first()
        name = request.form['name']
        size = request.form['size']
        path = request.form['path']
        image.name = name
        image.size = size
        image.path = path
        db.session.commit()
        return redirect('/image/edit/%s' % str(imageid))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10050, debug=True)
