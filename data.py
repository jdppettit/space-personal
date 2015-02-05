import pymongo
import datetime
import bson
import hashlib
import uuid

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

def encrypt_password(password):
    m = hashlib.sha256()
    m.update(password)
    config_rec = get_config()
    m.update(config_rec['password_salt'])
    return m.hexdigest()

def make_service(name):
    db = get_connect()
    service_cursor = db.service
    new_service = ({"name":name, "status":2})
    service_cursor.insert(new_service)

def make_admin(username, password):
    db = get_connect()
    admin_cursor = db.admin
    new_admin = ({"_id":username, "username":username, "password":encrypt_password(password)})
    admin_cursor.insert(new_admin)

def make_server(name, disk_size, disk_image, ram, vcpu):
    db = get_connect()
    server_cursor = db.server
    new_server = ({"name":name, "disk_size":disk_size, "disk_path":"", "ram":ram, "state":1, "disk_image":disk_image, "vcpu":vcpu, "inconsistent":0, "blocked":0})
    id = server_cursor.insert(new_server)
    disk_path = "%s/vm%s.img" % (str(config['disk_directory']), str(id))
    server_cursor.update({"_id":objectify(id)}, {"$set":{"disk_path":disk_path}})
    return id

def make_log(date, message, level):
    db = get_connect()
    log_cursor = db.log
    new_log = ({"date":date, "message":message, "level":level})
    log_cursor.insert(new_log)

def make_event(type, server_id, date, status=1, complete_date=""):
    if complete_date == "" and type != 6:
        complete_date = date
    db = get_connect()
    event_cursor = db.event
    new_event = ({"type":type, "server_id":str(server_id), "date":date, "status":status, "complete_date":complete_date})
    id = event_cursor.insert(new_event)
    return id

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
    db = get_connect()
    host_cursor = db.host
    new_host = ({"name":name})
    id = host_cursor.insert(new_host)
    return id

def make_configuration(image_directory, disk_directory, config_directory, system_type, domain, dhcp_configuration, dhcp_service, novnc_directory, pem_location):
    db = get_connect()
    config_cursor = db.configuration
    configuration = ({"_id":"default", "image_directory":image_directory, "disk_directory":disk_directory, "config_directory":config_directory, "system_type":system_type, "domain":domain, "password_salt":str(uuid.uuid1()), "dhcp_configuration":dhcp_configuration, "dhcp_service":dhcp_service, "novnc_directory":novnc_directory, "pem_location": pem_location})
    config_cursor.insert(configuration)

def make_iprange(startip, endip, subnet, netmask, gateway):
    db = get_connect()
    iprange_cursor = db.iprange
    iprange = ({"startip":startip, "endip":endip, "subnet":subnet, "netmask":netmask, "gateway":gateway})
    id = iprange_cursor.insert(iprange)
    return id

def make_host_statistic(cpu, memory_used, total_memory, iowait, date):
    db = get_connect()
    host_statistic_cursor = db.host_statistic
    statistic = ({"cpu":cpu, "memory_used":memory_used, "iowait":iowait, "date":date, "total_memory":total_memory})
    host_statistic_cursor.insert(statistic)

def get_all_iprange():
    db = get_connect()
    iprange_cursor = db.iprange
    ipranges = iprange_cursor.find() 
    return ipranges

def get_iprange_id(id):
    db = get_connect()
    iprange_cursor = db.iprange
    iprange = iprange_cursor.find({"_id":objectify(id)})
    return iprange

def get_host_statistic_all():
    db = get_connect()
    host_statistic_cursor = db.host_statistic
    statistics = host_statistic_cursor.find().sort("date",-1)
    return statistics

def get_host_statistic_specific(num):
    db = get_connect()
    host_statistic_cursor = db.host_statistic
    statistics = host_statistic_cursor.find().sort("date",-1).limit(num)
    return statistics 

def set_server_all(id, name, disk_size, disk_path, ram, state, disk_image, vcpu, mac_address, inconsistent = 0):
    db = get_connect()
    server_cursor = db.server
    server_cursor.update({"_id":objectify(id)}, {"name":name, "disk_size":disk_size, "disk_path":disk_path, "ram":ram, "state":state, "disk_image":disk_image, "vcpu":vcpu, "mac_address":mac_address, "inconsistent":inconsistent})

def get_server_id(id):
    db = get_connect()
    server_cursor = db.server
    server = server_cursor.find({"_id":objectify(id)})
    return server

def get_config():
    db = get_connect()
    config_cursor = db.configuration
    config = config_cursor.find_one()
    return config

def get_host_id(id):
    db = get_connect()
    host_cursor = db.host
    host = host_cursor.find({"_id":objectify(id)})
    return host

def get_image_id(id):
    db = get_connect()
    image_cursor = db.image
    image = image_cursor.find({"_id":objectify(id)})
    return image

def get_all_hosts():
    db = get_connect()
    host_cursor = db.host
    hosts = host_cursor.find()
    return hosts

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

def get_server_state(state):
    db = get_connect()
    server_cursor = db.server
    servers = server_cursor.find({"state":state})
    return servers


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

def get_ipaddress_free_all():
    db = get_connect()
    ipaddress_cursor = db.ipaddress
    ipaddress = ipaddress_cursor.find({"server_id":0})
    return ipaddress

def get_ipaddress_allocated_all():
    db = get_connect()
    ipaddress_cursor = db.ipaddress
    ipaddress = ipaddress_cursor.find({"server_id":{"$ne":0}})
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

def delete_image(id):
    db = get_connect()
    image_cursor = db.image
    image_cursor.remove({"_id":objectify(id)})

def set_host_memory(total, free):
    db = get_connect()
    host_cursor = db.host
    host = host_cursor.find()
    host_cursor.update({"_id":host[0]['_id']}, {"$set":{"memory_total":total, "memory_free":free}})

def set_host_cpu(cpu, iowait):
    db = get_connect()
    host_cursor = db.host
    host = host_cursor.find()
    host_cursor.update({"_id":host[0]['_id']}, {"$set":{"cpu_total":cpu, "iowait":iowait}})

def delete_iprange(id):
    db = get_connect()
    iprange_cursor = db.iprange
    iprange_cursor.remove({"_id":objectify(id)})

def set_iprange_all(id, startip, endip, subnet, netmask, gateway):
    db = get_connect()
    iprange_cursor = db.iprange
    iprange_cursor.update({"_id":objectify(id)}, {"startip":startip, "endip":endip, "subnet":subnet, "netmask":netmask, "gateway":gateway})

def get_iprange_id(id):
    db = get_connect()
    iprange_cursor = db.iprange
    iprange = iprange_cursor.find({"_id":objectify(id)})
    return iprange

def get_log_datelevel(date = "", level = 0):
    db = get_connect()
    log_cursor = db.log
    log = ""
    now = datetime.datetime.now()
    if date == "" and level != "":
        level = int(level)
        log = log_cursor.find({"level":level})
        return log
    elif date != "" and level == 0:
        if date == "day":
            one_day = now - datetime.timedelta(days=1)
            log = log_cursor.find({"date": {"$gt":one_day}})
            return log
        elif date == "week":
            one_week = now - datetime.timedelta(days=7)
            log = log_cursor.find({"date": {"$gt":one_week}})
            return log
        elif date == "month":
            one_month = now - datetime.timedelta(days=30)
            log = log_cursor.find({"date": {"$gt":one_month}})
            return log
        elif date == "all":
            log = log_cursor.find()
            return log
    elif date != "" and level != "":
        if date == "day":
            one_day = now - datetime.timedelta(days=1)
            log = log_cursor.find({"date": {"$gt":one_day}, "level":level})
            return log
        elif date == "week":
            one_week = now - datetime.timedelta(days=7)
            log = log_cursor.find({"date": {"$gt":one_week}, "level":level})
            return log
        elif date == "month":
            one_month = now - datetime.timedelta(days=30)
            log = log_cursor.find({"date": {"$gt":one_month}, "level":level})
            return log
        elif date == "all":
            log = log_cursor.find()
            return log

def set_configuration_all(system, domain, disk_directory, image_directory, config_directory, dhcp_configuration, dhcp_service, novnc_directory, pem_location):
    db = get_connect()
    config_cursor = db.configuration
    config_cursor.update({"_id":"default"}, {"$set": {"system_type":system, "domain":domain, "disk_directory":disk_directory, "image_directory":image_directory, "config_directory":config_directory, "dhcp_configuration":dhcp_configuration, "dhcp_service":dhcp_service, "novnc_directory":novnc_directory, "pem_location":pem_location}})

def get_admin(username):
    db = get_connect()
    admin_cursor = db.admin
    admin = admin_cursor.find({"_id":username})
    return admin

def get_service_all():
    db = get_connect()
    service_cursor = db.service
    services = service_cursor.find()
    return services

def update_admin(username, password):
    db = get_connect()
    admin_cursor = db.admin
    admin_cursor.update({"_id":username}, {"$set": {"password": encrypt_password(password) }})

def set_server_disksize(vmid, size):
    db = get_connect()
    server_cursor = db.server
    server_cursor.update({"_id":objectify(vmid)}, {"$set":{"disk_size":size}})

def set_event_status(id, status):
    db = get_connect()
    event_cursor = db.event
    event_cursor.update({"_id":objectify(id)}, {"$set": {"status":status}})

def set_event_complete(id, date):
    db = get_connect()
    event_cursor = db.event
    event_cursor.update({"_id":objectify(id)}, {"$set": {"complete_date":date}})

def set_server_blocked(id, blocked):
    db = get_connect()
    server_cursor = db.server
    server_cursor.update({"_id":objectify(id)}, {"$set": {"blocked":blocked}})
