import pymongo
import datetime
import config 
#import utils
import bson

def objectify(id):
    id_obj = bson.objectid.ObjectId(id)
    return id_obj

def get_connect():
    con = pymongo.MongoClient()
    db = con.space
    if con:
        return db
    else:
        print "Failed to get DB connection."

def make_server(name, disk_size, disk_image, ram, vcpu):
    db = get_connect()
    server_cursor = db.server
    new_server = ({"name":name, "disk_size":disk_size, "disk_path":"", "ram":ram, "state":1, "disk_image":disk_image, "vcpu":vcpu, "inconsistent":0})
    id = server_cursor.insert(new_server)
    disk_path = "%s/%s.img" % (str(config.image_path), str(id))
    server_cursor.update({"_id":objectify(id)}, {"$set":{"disk_path":disk_path}})
    return id

def make_log(date, message, level):
    db = get_connect()
    log_cursor = db.log
    new_log = ({"date":date, "message":message, "level":level})
    log_cursor.insert(new_log)

def make_event(type, server_id, date):
    db = get_connect()
    event_cursor = db.event
    new_event = ({"type":type, "server_id":server_id, "date":date})
    event_cursor.insert(new_event)

def make_image(name, path, size):
    db = get_connect()
    image_cursor = db.image
    new_image = ({"name":name, "path":path, "size":size})
    image_cursor.insert(new_image)

def make_ipaddress(ip, netmask, server_id):
    db = get_connect()
    ipaddress_cursor = db.ipaddress
    new_ipaddress = ({"ip":ip, "netmask":netmask, "server_id":server_id})
    ipaddress_cursor.insert(new_ipaddress)

def make_host(name):
    db = get_conect()
    host_cursor = db.host
    new_host = ({"name":name})
    host_cursor.insert(new_host)

def get_server_id(id):
    db = get_connect()
    server_cursor = db.server
    server = server_cursor.find({"_id":objectify(id)})
    return server

def get_image_id(id):
    db = get_connect()
    image_cursor = db.image
    image = image_cursor.find({"_id":objectify(id)})
    return image

def set_server_mac(id, mac_address):
    db = get_connect()
    server_cursor = db.server
    server_cursor.update({"_id":objectify(id)}, {"$set":{"mac_address":mac_address}})

def set_image_all(id, name, path, size):
    db = get_connect()
    image_cursor = db.image
    image_cursor.update({"_id":objectify(id)}, {"name":name, "path":path, "size":size})

def set_ipaddress_all(id, ip, netmask, server_id):
    db = get_connect()
    ipaddress_cursor = db.ipaddress
    ipaddress_cursor.update({"_id":objectify(id)}, {"ip":ip, "netmask":netmask, "server_id":server_id})

def set_ipaddress_serverid(id, server_id):
    db = get_connect()
    ipaddress_cursor = db.ipaddress
    ipaddress_cursor.update({"_id":objectify(id)}, {"$set":{"server_id":server_id}})

def get_all_servers(not_state = 0):
    db = get_connect()
    server_cursor = db.server
    servers = ""

    if not_state != 0:
        servers = server_cursor.find({"state": { "$ne":not_state}})
    else:
        servers = server_cursor.find()
    
    return servers

def get_all_logs(min_level = 0):
    db = get_connect()
    log_cursor = db.log
    logs = ""

    if min_level != 0:
        logs = log_cursor.find({"level": {"$gt":min_level}})
    else:
        logs = log_cursor.find()

    return logs

def get_all_images():
    db = get_connect()
    image_cursor = db.image
    images = ""
    images = image_cursor.find()
    return images

def get_events_server(vmid):
    db = get_connect()
    event_cursor = db.event
    events = event_cursor.find({"server_id":vmid})
    return events

def get_ipaddress_server(vmid):
    db = get_connect()
    ipaddress_cursor = db.ipaddress
    ipaddress = ipaddress_cursor.find({"server_id":vmid})
    return ipaddress

def get_all_ipaddress():
    db = get_connect()
    ipaddress_cursor = db.ipaddress
    ipaddresses = ipaddress_cursor.find()
    return ipaddresses

def get_ipaddress(id):
    db = get_connect()
    ipaddress_cursor = db.ipaddress
    ipaddress = ipaddress_cursor.find({"_id":objectify(id)})
    return ipaddress

def get_image(id):
    db = get_connect()
    image_cursor = db.image
    image = image_cursor.find({"_id":objectify(id)})
    return image

def get_ipaddress_free():
    db = get_connect()
    ipaddress_cursor = db.ipaddress
    ipaddress = ipaddress_cursor.find_one({"server_id":0})
    return ipaddress

def delete_ipaddress(id):
    db = get_connect()
    ipaddress_cursor = db.ipaddress
    ipaddress_cursor.remove({"_id":objectify(id)})

def set_server_state(id, state):
    db = get_connect()
    server_cursor = db.server
    server_cursor.update({"_id":objectify(id)}, {"$set":{"state":state}})

def set_server_inconsistent(id, inconsistent):
    db = get_connect()
    server_cursor = db.server
    server_cursor.update({"_id":objectify(id)}, {"$set":{"inconsistent":inconsistent}})
