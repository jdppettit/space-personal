import pymongo
import datetime
import config 
#import utils

def build_id_query(id):
    query = ({"_id":"ObjectID\(\"%s\"\)"} % str(id))
    return query

def objectify(id):
    id_obj = pymongo.ObjectID(id)
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
    new_server = ({"name":name, "disk_size":disk_size, "disk_path":"", "ram":ram, "state":1, "disk_image":disk_image, "vcpu":vcpu})
    id = server_cursor.insert(new_server)
    disk_path = "%s/%s.img" % (str(config.image_path), str(id))
    server_cursor.update({"_id":objectify(id)}, {"disk_path":disk_path})
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
    query = build_id_query(id)
    server = server_cursor.find(query)
    return server

def get_image_id(id):
    db = get_connect()
    image_cursor = db.image
    query = build_id_query(id)
    image = image_cursor.find(query)
    return image
