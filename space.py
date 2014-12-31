from flask import *
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.basicauth import BasicAuth

from config import *

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

    def __init__(self, name, disk_size, disk_path, ram, state):
        self.name = name
        self.disk_size = disk_size
        self.disk_path = disk_path
        self.ram = ram
        self.state = state

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

db.create_all()
db.session.commit()


def connect():
    conn=libvirt.open("qemu:///system")
    print "[%s] Connection established with server." % str(datetime.datetime.now())    
    return conn

def list_vms():
    conn = connect()
    other_domains = conn.listDefinedDomains()
    running_domains = conn.listDomainsID()
    print "[%s] Got a list of domains." % str(datetime.datetime.now())
    data = []
    for id in running_domains:
        data.append(conn.lookupByID(id))
    return data, other_domains

def shutdown_vm(name):
    conn = connect()
    print "[%s] Sent shutdown to VM %s." % (str(datetime.datetime.now()), str(name))
    vm = conn.lookupByName(name)
    vm.destroy()

def start_vm(name):
    conn = connect()
    print "[%s] Sent startup to VM %s." % (str(datetime.datetime.now()), str(name))
    vm = conn.lookupByName(name)
    vm.create()

def create_vm(name, ram, disk_size):
    string = "virt-install --name %s --ram %s --disk path=/var/disks/%s.img,size=%s --vnc --cdrom /var/images/ubuntu-14.04.1-server-amd64.iso" % (str(name), str(ram), str(name), str(disk_size))
    process = subprocess.Popen(string.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print "[%s] Created new VM with name %s %sMB/%sGB image %s.img." % (str(datetime.datetime.now()), str(name), str(ram), str(disk_size), str(name))
    print output

@app.route('/')
def index():
    running_domains, other_domains = list_vms()
    return render_template("index.html", running_domains = running_domains, other_domains = other_domains)

@app.route('/create', methods=['POST'])
def create():
    name = request.form['name']
    ram = request.form['ram']
    disk_size = request.form['disk_size']
    new_vm = Server(name, disk_size, "", ram, 0)
    db.session.add(new_vm)
    db.session.commit()
    create_vm(name, ram, disk_size)
    return redirect('/')

@app.route('/shutdown/<vmname>')
def shutdown(vmname):
    shutdown_vm(vmname)
    return redirect('/')

@app.route('/start/<vmname>')
def start(vmname):
    start_vm(vmname)
    return redirect('/')

@app.route('/images', methods=['POST','GET'])
def images():
    if request.method == "GET":
        images = Image.query.all()
        return render_template("images.html", images=images)
    else:
        new_image = Image(request.form['name'], request.form['path'], request.form['size'])
        db.session.add(new_image)
        db.session.commit()
        return redirect('/images')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10050, debug=True)
