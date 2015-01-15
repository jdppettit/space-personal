import libvirt
import datetime
import os
import subprocess
import create
import xml.etree.ElementTree as et

from log import *
from event import *
from config import *
from models import db, Log, IPAddress, Server

def restart_dhcpd():
    command = "service dhcpd restart"
    ip = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    create_log("Restarted DHCPD.", 1)


def connect():
    conn=libvirt.open("%s:///system" % system_type)
    message = "Connection established with server."
    logm = Log(str(datetime.datetime.now()), message, 1)
    db.session.add(logm)
    db.session.commit()
    return conn

def list_vms():
    conn = connect()
    other_domains = conn.listDefinedDomains()
    running_domains = conn.listDomainsID()
    message =  "Got a list of domains."
    db.session.add(logm)
    db.session.commit()
    data = []
    for id in running_domains:
        data.append(conn.lookupByID(id))
    return data, other_domains

def shutdown_vm(name):
    conn = connect()
    message = "Sent shutdown to vm%s." % str(name)
    create_log(message, 1)
    vm = conn.lookupByName("vm%s" % str(name))
    try:
        vm.destroy()
    except:
        message2 = "Attempted to shutdown vm%s, but it wasn't running." % str(name)
        create_log(message2, 2)

def start_vm(name):
    conn = connect()
    message = "Sent startup to vm%s." % str(name)
    logm = Log(str(datetime.datetime.now()), message, 1)
    db.session.add(logm)
    db.session.commit()
    vm = conn.lookupByName("vm%s" % str(name))
    vm.create()

def create_vm(name, ram, disk_size, image, vcpu):
    create.make_config(name, "", ram, vcpu, image)
    message = "Created new configuration for vm%s at %s/vm%s.xml" % (str(name), str(config_path), str(name))
   
    create_log(message, 1)

    create.make_image(name, disk_size)
    message2 = "Created new disk image %s/vm%s.img of size %sGB." % (str(name), str(disk_path), str(disk_size))
    
    create_log(message2, 1)

    conn = connect()
    xmlpath = "%s/vm%s.xml" % (str(config_path), str(name))
    
    xml = ""

    with open(xmlpath, "r") as file:
        xml = file.read()

    conn.defineXML(xml)

    message3 = "Defined new domain vm%s." % str(name)
    create_log(message3, 1)

    newdom = conn.lookupByName("vm%s" % str(name))
    newdom.create()

    message4 = "Sent startup to vm%s." % str(name)
    create_log(message4, 1)

def update_config(vm):
    os.remove('%s/vm%s.xml') % (str(config_path), str(vm.id))
    
    message1 = "Deleted config for vm%s at %s/vm%s.xml" % (str(vm.id), str(config_path), str(vm.id))
    logm1 = Log(datetime.datetime.now(), message1, 1)
    db.session.add(logm1)
    
    create.make_config(vm.id, "", str(vm.ram), str(vm.vcpu), vm.image)

    message = "Created new configuration for vm%s at %s/vm%s.xml" % (str(vm.id), str(config_path), str(vm.id))

    logm2 = Log(datetime.datetime.now(), message, 1)
    db.session.add(logm2)

    db.session.commit()

def redefine_vm(vm):
    conn = connect()
    dom = conn.lookupByName("vm%s" % str(vm.id))
    try:
        dom.destroy()
    except:
        dom.undefine()

    xmlpath = "%s/vm%s.xml" % (str(config_path), str(vm.id))

    xml = ""

    with open(xmlpath, "r") as file:
            xml = file.read()

    conn.defineXML(xml)

    message3 = "Redefined domain vm%s." % str(vm.id)
    logm3 = Log(datetime.datetime.now(), message3, 1)
    db.session.add(logm3)

    db.session.commit()



def delete_vm(name, image_path):
    conn = connect()
    vm = conn.lookupByName("vm%s" % str(name))
    try:
        vm.destroy()
    except:
        vm.undefine()
    os.remove(image_path)
    message = "Deleted VM with name vm%s, image removed at %s." % (str(name), str(image_path))
    logm = Log(str(datetime.datetime.now()), message, 1)
    db.session.add(logm)
    db.session.commit()

def make_console(name):
    try:
        port, endport = get_vnc_port(name)
        novncport = start_novnc(port, endport)
        return novncport
    except Exception as e:
        message = "Failed to create VNC console. Got message: %s" % str(e)
        create_log(message, 3)
        return "error" 


def get_vnc_port(name):
    conn = connect()
    vm = conn.lookupByName("vm%s" % str(name))
    command = "virsh vncdisplay vm%s" % str(name)
    p = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = p.communicate()[0]
    endport = output.split(":")[1]
    if int(endport) < 10:
        port = "590%s" % str(endport)
        eport = "0%s" % str(endport)
    else:
        port = "59%s" % str(endport)
        eport = endport
    message = "Got VNC port %s, output returned: %s" % (str(port), str(output))
    create_log(message, 1)
    return port, eport

def start_novnc(port, last):
    command = "python /srv/noVNC/utils/websockify --web /srv/noVNC 61%s localhost:%s -D" % (str(last), str(port))
    command = command.replace('\n', '')
#    command = "/srv/noVNC/utils/websockify 127.0.0.1:60%s --vnc 127.0.0.1:%s --web /srv/noVNC/utils -D" % (str(last), str(port))
    p = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = p.communicate()[0]
    message = "Opened noVNC on port 60%s" % str(last)
    create_log(message, 1)
    port = "61%s" % str(last)
    return port

def assign_ip(vmid):
    available_ips = data.get_ipaddress_free()
    if not available_ips:
        create_log("Attempted to assign an IP address, but no IP addresses remained.", 2)
        return 0
    data.set_ipaddress_serverid(vmid, vmid)
    return available_ips['ip']

def append_dhcp_config(mac_address, ip, vmid):
    with open("/etc/dhcp/dhcpd.conf", "a") as config:
        config.write("host vm%s {\n hardware ethernet %s;\n fixed-address %s;\n}" % (str(vmid), str(mac_address), str(ip)))
        config.close()
    restart_dhcpd()

def rebuild_dhcp_config():
    ips = IPAddress.query.filter(IPAddress.server_id != 0).all()
    create_log("Rebuilding DHCPD configuration to unassign IP.", 1)
    with open("/etc/dhcp/dhcpd.conf", "w") as config:
        config.write("option domain-name-servers 8.8.8.8, 8.8.4.4;\n\n")
        config.write("subnet 198.204.234.136 netmask 255.255.255.248 {\n range 198.204.234.139 198.204.234.142;\n option routers 198.204.234.137;\n}\n")
        for ip in ips:
            vm = Server.query.filter_by(id=ip.server_id).first()
            config.write("host vm%s {\n hardware ethernet %s;\n fixed-address %s;\n}\n" % (str(vm.id), str(vm.mac_address), str(ip.ip)))
        config.close()
    restart_dhcpd()    

def get_guest_mac(name):
    conn = connect()
    vm = conn.lookupByName("vm%s" % str(name))
    vm_xml = vm.XMLDesc(0)
    tree = et.fromstring(vm_xml)
    mac_address = ""

    for child in tree:
        print child
        if child.tag == "devices":
            for sub in child:
                print sub
                if sub.tag == "interface":
                    for ssub in sub:
                        print ssub
                        if ssub.tag == "mac":
                            mac_address = ssub.attrib

    return mac_address['address']
