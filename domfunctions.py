import libvirt
import datetime
import os
import subprocess

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

def create_vm(name, ram, disk_size, image_path):
    string = "virt-install --name vm%s --ram %s --disk path=/var/disks/vm%s.img,size=%s --vnc --cdrom %s" % (str(name), str(ram), str(name), str(disk_size), str(image_path))
    process = subprocess.Popen(string.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    message = "Created new VM with name %s %sMB/%sGB image %s.img." % (str(name), str(ram), str(disk_size), str(name))
    logm = Log(str(datetime.datetime.now()), message, 1)
    db.session.add(logm)
    db.session.commit()
    print output

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

