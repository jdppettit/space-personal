import libvirt
import datetime

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

def create_vm(name, ram, disk_size, image_path):
    string = "virt-install --name %s --ram %s --disk path=/var/disks/%s.img,size=%s --vnc --cdrom %s" % (str(name), str(ram), str(name), str(disk_size), str(image_path))
    process = subprocess.Popen(string.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print "[%s] Created new VM with name %s %sMB/%sGB image %s.img." % (str(datetime.datetime.now()), str(name), str(ram), str(disk_size), str(name))
    print output


