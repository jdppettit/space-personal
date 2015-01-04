import libvirt
import datetime
import os
import subprocess
import create

from space import db, Log

def connect():
    conn=libvirt.open("qemu:///system")
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
    logm = Log(str(datetime.datetime.now()), message, 1)
    db.session.add(logm)
    db.session.commit()
    vm = conn.lookupByName("vm%s" % str(name))
    vm.destroy()

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
    message = "Created new configuration for vm%s at /var/config/vm%s.xml" % (str(name), str(name))
    
    logm1 = Log(datetime.datetime.now(), message, 1)
    db.session.add(logm1)

    create.make_image(name, disk_size)
    message2 = "Created new disk image /var/disks/vm%s.img of size %sGB." % (str(name), str(disk_size))

    logm2 = Log(datetime.datetime.now(), message2, 1)
    db.session.add(logm2)

    conn = connect()
    xmlpath = "/var/configs/vm%s.xml" % str(name)
    
    xml = ""

    with open(xmlpath, "r") as file:
        xml = file.read()

    conn.defineXML(xml)

    message3 = "Defined new domain vm%s." % str(name)
    logm3 = Log(datetime.datetime.now(), message3, 1)
    db.session.add(logm3)

    newdom = conn.lookupByName("vm%s" % str(name))
    newdom.create()

    message4 = "Sent startup to vm%s." % str(name)
    logm4 = Log(datetime.datetime.now(), message4, 1)
    db.session.add(logm4)

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
    port, endport = get_vnc_port(name)
    novncport = start_novnc(port, endport)
    return novncport

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
    logm = Log(datetime.datetime.now(), message, 1)
    db.session.add(logm)
    db.session.commit()
    return port, eport

def start_novnc(port, last):
    command = "python /srv/noVNC/utils/websockify --web /srv/noVNC 61%s localhost:%s -D" % (str(last), str(port))
    command = command.replace('\n', '')
    print command
#    command = "/srv/noVNC/utils/websockify 127.0.0.1:60%s --vnc 127.0.0.1:%s --web /srv/noVNC/utils -D" % (str(last), str(port))
    p = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = p.communicate()[0]
    message = "Opened noVNC on port 60%s" % str(last)
    logm = Log(datetime.datetime.now(), message, 1)
    db.session.add(logm)
    db.session.commit()
    port = "61%s" % str(last)
    return port



