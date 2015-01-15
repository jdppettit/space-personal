from flask import *
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.basicauth import BasicAuth

from config import *
from domfunctions import *
from models import *
from event import *
from cron import *
from log import *
from data import *

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

db.create_all()
db.session.commit()

@app.route('/tests/mac')
def tests_mac():
    print get_guest_mac(7)

@app.route('/utils/sync_status')
def syncstatus():
   sync_status()
   return redirect('/')

@app.route('/utils/import_images')
def importimages():
    import_images()
    return redirect('/')

@app.route('/console/<vmid>')
def console(vmid):
    vm = get_server_id(vmid)
    vncport = make_console(str(vmid))    
    return render_template("vnc_auto.html", port=vncport, server_name=vm[0]['name'])

@app.route('/ip', methods=['POST','GET'])
def ips():
    if request.method == "GET":
        ips = get_all_ipaddress() 
        return render_template("ips.html", ips=ips)
    else:
        address = request.form['address']
        netmask = request.form['netmask']
        new_ip = make_ipaddress(address, netmask, 0)
        message = "Added new IP %s/%s" % (str(address), str(netmask))
        create_log(message, 1)
        return redirect('/ip')

@app.route('/ip/edit/<ipid>', methods=['POST','GET'])
def ip_edit(ipid):
    if request.method == "GET":
        ip = get_ipaddress(ipid)
        return render_template("edit_ip.html", ip=ip)
    elif request.method == "POST":
        set_ipaddress_all(ipid, request.form['address'], request.form['netmask'], request.form['server_id'])
        return redirect('/ip/edit/%s' % str(ipid))

@app.route('/ip/unassign/<ipid>', methods=['GET'])
def ip_unassign(ipid):
    set_ipaddress_serverid(ipid, 0)
    rebuild_dhcp_config()
    return redirect('/ip')

@app.route('/ip/assign/<vmid>', methods=['POST'])
def ip_assign(vmid):
    ip_id = request.form['ip']
    set_ipaddress_serverid(ipid, vmid)
    rebuild_dhcp_config()
    return redirect('/edit/%s' % str(vmid))

@app.route('/ip/delete/<ipid>', methods=['GET'])
def ip_delete(ipid):
    set_ipaddress_serverid(ipid, 0)
    rebuild_dhcp_config()
    delete_ipaddress(ipid)
    redirect('/ip')

@app.route('/events')
def events():
    log = get_all_logs() 
    return render_template("events.html", log=log)

@app.route('/')
def index():
    servers = get_all_servers(not_state = 3)
    log = get_all_logs(min_level = 2)
    images = get_all_images()
    return render_template("index.html", servers = servers, images=images, log=log)

@app.route('/create', methods=['POST'])
def create():
    name = request.form['name']
    ram = request.form['ram']
    disk_size = request.form['disk_size']
    image = request.form['image']
    vcpu = request.form['vcpu']

    image_obj = get_image_id(image) 
    
    new_vm = make_server(name, disk_size, image_obj[0]['name'], ram, vcpu)
    
    result = assign_ip(new_vm)

    if result == 0:
        return "Failed."
    
    create_event(new_vm)
    startup_event(new_vm)
    create_vm(new_vm, ram, disk_size, image_obj[0]['name'], vcpu)
    
    mac_address = get_guest_mac(new_vm)

    set_server_mac(new_vm, mac_address)

    append_dhcp_config(mac_address, result, new_vm)

    message = "Created a new VM with ID %s, name of %s, %sMB of RAM, %sGB disk image." % (str(new_vm), str(name), str(ram), str(disk_size))
    create_log(message, 1)

    db.session.commit()

    return redirect('/')

@app.route('/destroy/<vmid>')
def destroy(vmid):
    vm = get_server_id(vmid)
    ip = get_ipaddress_server(vmid)
    
    try:
        set_ipaddress_serverid(ip[0]['_id'], 0)
    except:
        pass

    rebuild_dhcp_config()
    
    set_server_state(vmid, 3)
    destroy_event(vmid)
    delete_vm(vmid, vm['disk_path'])

    message = "Deleted vm%s." % str(vmid)
    create_log(message, 1)

    return redirect('/')

@app.route('/reboot/<vmid>')
def reboot(vmid):
    set_server_state(vmid, 0)
    set_server_inconsistent(vmid, 0)

    shutdown_event(vmid)
    shutdown_vm(vmid)
   
    set_server_state(vmid, 1)

    startup_event(vmid)
    start_vm(vmid)

    return redirect('/')

@app.route('/shutdown/<vmid>')
def shutdown(vmid):
    set_server_state(vmid, 0)
    set_server_inconsistent(vmid, 0)

    shutdown_event(vmid)
    shutdown_vm(vmid)

    return redirect('/')

@app.route('/start/<vmid>')
def start(vmid):
    set_server_state(vmid, 1)
    set_server_inconsistent(vmid, 0)
    
    startup_event(vmid)
    start_vm(vmid)

    return redirect('/')

@app.route('/vms/all')
def view_all():
    domains = get_all_servers()
    return render_template("view.html", domains=domains, type="all")

@app.route('/vms/active')
def view_active():
    domains = get_all_servers(not_state = 3)
    return render_template("view.html", domains=domains, type="active")

@app.route('/vms/deleted')
def view_deleted():
    domains = get_server_state(3)
    try:
        print domains[0]
    except:
        domains = None
    return render_template("view.html", domains=domains, type="deleted")

@app.route('/host', methods=['POST','GET'])
def host():
    if request.method == "GET":
        host = get_all_hosts()
        try:
            print host[0]['name']
        except:
            host_id = make_host("default")
            host = get_host_id(host_id)
        return render_template("host.html", host=host)
    elif request.method == "POST":
        host = Host.query.first()
        host.name = request.form['hostname']
        host.ram = int(request.form['ram_total'])
        db.session.merge(host)
        db.session.commit()
        return redirect('/host')

@app.route('/edit/<vmid>', methods=['POST','GET'])
def edit(vmid):
    if request.method == "GET":
        server = get_server_id(vmid)
        events = get_events_server(vmid)
        my_ip = get_ipaddress_server(vmid)
        ips = get_all_ipaddress()
        try:
            print my_ip[0]
        except:
            my_ip = None
        return render_template("edit.html", server=server, events=events, my_ip=my_ip, ips=ips)
    elif request.method == "POST":
        set_server_all(vmid, request.form['name'], request.form['disk_size'], request.form['disk_path'],
        request.form['ram'], request.form['state'], request.form['image'], request.form['vcpu'],
        request.form['mac_address'])
        
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
        images = get_all_images()
        return render_template("images.html", images=images)
    else:
        new_image = make_image(request.form['name'], request.form['path'], request.form['size'])
        message = "Created new image %s" % str(new_image)
        create_log(message, 1)
        return redirect('/images')

@app.route('/image/edit/<imageid>', methods=['POST','GET'])
def edit_image(imageid):
    if request.method == "GET":
        image = get_image(imageid)
        return render_template("edit_image.html", image=image)
    else:
        image = Image.query.filter_by(id=imageid).first()
        name = request.form['name']
        size = request.form['size']
        path = request.form['path']
        set_image_all(imageid, name, path, size)
        return redirect('/image/edit/%s' % str(imageid))

@app.route('/image/delete/<imageid>')
def delete_image_route(imageid):
    delete_image(imageid)
    return redirect('/images')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10051, debug=True)
