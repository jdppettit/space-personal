from models import db, Server, Log, Event
from event import *
from log import *
from domfunctions import connect 

import libvirt
import datetime

def sync_status():
    conn = connect()
    real_status = conn.listDefinedDomains()

    servers = Server.query.all()

    message_sync = "Syncing real state with database states."
    create_log(message_sync, 1)

    for server in servers:
        real_id = "vm%s" % str(server.id)
        if server.state == 0 and real_id not in real_status:
            message = "Checked %s, DB says it should not be running, but it is running." % real_id
            create_log(message, 2)

            inconsistent_event(server.id)

            server.inconsistent = 1
            db.session.add(server)
            db.session.commit()
        elif server.state == 1 and real_id in real_status:
            message = "Checked %s, DB says it should be running, but is is not running." % real_id
            create_log(message, 2)
            
            inconsistent_event(server.id)

            server.inconsistent = 1
            db.session.add(server)
            db.session.commit()
