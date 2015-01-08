from space import db, Server, Log

import libvirt
import datetime

def sync_status():
    conn = domfunctions.connect()
    real_status = conn.listDefinedDomains()    

    servers = Server.query.all()
    
    message_sync = "Syncing real state with database states."
    logm_sync = Log(datetime.datetime.now(), message_sync, 1)
    db.session.add(logm_sync)
    db.session.commit()

    for server in servers:
        real_id = "vm%s" % str(server.id)
        if server.state == 0 and real_id in real_status:
            message = "Checked %s, DB says it should not be running, but it is running." % real_id
            logm = Log(datetime.datetime.now(), message, 2)
            db.session.add(logm)
            server.inconsistent = 1
            db.session.commit()
        elif server.state == 1 and real_id not in real_status:
            message = "Checked %s, DB says it should be running, but is is not running." % real_id
            logm = Log(datetime.datetime.now(), message, 2)
            db.session.add(logm)
            server.inconsistent = 1
            db.session.commit()




