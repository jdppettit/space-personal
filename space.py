from flask import *
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.basicauth import BasicAuth

from config import *
from domfunctions import *
from models import *
from event import *
from cron import *
from log import *

import libvirt
import subprocess
import datetime

app = Flask(__name__)

db.init_app(app)

connectionString = "mysql+mysqlconnector://%s:%s@%s:3306/%s" % (username, password, hostname, database)
app.config['SQLALCHEMY_DATABASE_URI'] = connectionString
db = SQLAlchemy(app)

app.config['BASIC_AUTH_USERNAME'] = ba_username
app.config['BASIC_AUTH_PASSWORD'] = ba_password
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)

'''
Event Types
1 = Create
2 = Destroy
3 = Boot
4 = Shutdown
5 = Inconsistency
'''

with app.app_context():
    db.create_all()
    db.session.commit()

@app.route('/tests/mac')
def tests_mac():
    print get_guest_mac(7)

@app.route('/utils/sync_status')
def syncstatus():
   sync_status()
   return redirect('/')

@app.route('/console/<vmid>')
def console(vmid):
    vm = Server.query.filter_by(id=vmid).first()
    vncport = make_console(str(vm.id))    
    return render_template("vnc_auto.html", port=vncport, server_name=vm.name)

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

@app.route('/ip/edit/<ipid>', methods=['POST','GET'])
def ip_edit(ipid):
    if request.method == "GET":
        ip = IPAddress.query.filter_by(id=ipid).first()
        return render_template("edit_ip.html", ip=ip)
    elif request.method == "POST":
        ip = IPAddress.query.filter_by(id=ipid).first()
        ip.address = request.form['address']
        ip.netmask = request.form['netmask']
        db.session.commit()
        return redirect('/ip/edit/%s' % str(ipid))

@app.route('/ip/unassign/<ipid>', methods=['GET'])
def ip_unassign(ipid):
    ip = IPAddress.query.filter_by(id=ipid).first()
    ip.server_id = 0
    db.session.commit()
    rebuild_dhcp_config()
    return redirect('/ip')

@app.route('/events')
def events():
    log = Log.query.all()
    return render_template("events.html", log=log)

@app.route('/')
def index():
    servers = Server.query.filter(Server.state != 3).all()
    log = Log.query.filter(Log.level >= 2).all()
    images = Image.query.all()
    return render_template("index.html", servers = servers, images=images, log=log)

@app.route('/create', methods=['POST'])
def create():
    name = request.form['name']
    ram = request.form['ram']
    disk_size = request.form['disk_size']
    image = request.form['image']
    vcpu = request.form['vcpu']
    
    image_obj = Image.query.filter_by(id=image).first()
    
    new_vm = Server(name, disk_size, "", ram, 1, image_obj.name, vcpu)
    
    db.session.add(new_vm)
    db.session.commit()
    db.session.refresh(new_vm)

    new_vm.disk_path = "/var/disks/vm%s.img" % str(new_vm.id)
    
    result = assign_ip(new_vm.id)

    if result == 0:
        return "Failed."
    
    create_event(new_vm.id)
    startup_event(new_vm.id)
    create_vm(new_vm.id, ram, disk_size, image_obj.name, vcpu)
    
    mac_address = get_guest_mac(new_vm.id)
    new_vm.mac_address = mac_address

    append_dhcp_config(mac_address, result, new_vm.id)

    message = "Created a new VM with ID %s, name of %s, %sMB of RAM, %sGB disk image." % (str(new_vm.id), str(name), str(ram), str(disk_size))
    create_log(message, 1)

    db.session.commit()

    return redirect('/')

@app.route('/destroy/<vmid>')
def destroy(vmid):
    vm = Server.query.filter_by(id=vmid).first()
    vm.state = 3
    destroy_event(vm.id)
    delete_vm(vm.id, vm.disk_path)

    message = "Deleted vm%s." % str(vmid)
    create_log(message, 1)

    db.session.commit()

    return redirect('/')

@app.route('/reboot/<vmid>')
def reboot(vmid):
    vm = Server.query.filter_by(id=vmid).first()
    vm.state = 0
    vm.inconsistent = 0

    db.session.commit()

    shutdown_event(vm.id)
    shutdown_vm(vm.id)
    
    vm.state = 1

    db.session.commit()

    startup_event(vm.id)
    start_vm(vm.id)

    return redirect('/')

@app.route('/shutdown/<vmid>')
def shutdown(vmid):
    vm = Server.query.filter_by(id=vmid).first()
    vm.state = 0
    vm.inconsistent = 0

    shutdown_event(vm.id)
    shutdown_vm(vm.id)

    db.session.commit()

    return redirect('/')

@app.route('/start/<vmid>')
def start(vmid):
    vm = Server.query.filter_by(id=vmid).first()
    vm.state = 1
    vm.inconsistent = 0
    
    startup_event(vm.id)
    start_vm(vm.id)
    
    db.session.commit()

    return redirect('/')

@app.route('/vms/all')
def view_all():
    domains = Server.query.all()
    return render_template("view.html", domains=domains, type="all")

@app.route('/vms/active')
def view_active():
    domains = Server.query.filter(Server.state != 3).all()
    return render_template("view.html", domains=domains, type="active")

@app.route('/vms/deleted')
def view_deleted():
    domains = Server.query.filter_by(state=3).all()
    return render_template("view.html", domains=domains, type="deleted")

@app.route('/host', methods=['POST','GET'])
def host():
    if request.method == "GET":
        return render_template("host.html")
    else:
        print "foo"

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

        if "push" in request.form:
            # We're going to actually update the config
            update_config(vm) 
            try:
                shutdown_event(vm.id)
                shutdown_vm(vm.id)
            except:
                pass
            redefine_vm(vm)
            if vm.state == 1:
                start_vm(vm.id)
                startup_event(vm.id)
        return redirect('/edit/%s' % str(vmid))

@app.route('/images', methods=['POST','GET'])
def images():
    if request.method == "GET":
        images = Image.query.all()
        return render_template("images.html", images=images)
    else:
        new_image = Image(request.form['name'], request.form['path'], request.form['size'])
        message = "Created new image %s of size %s at %s" % (str(new_image.name), str(new_image.size), str(new_image.path))
        create_log(message, 1)
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
    app.run(host='0.0.0.0', port=10051, debug=True)
