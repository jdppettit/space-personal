from models import db, Event

import datetime

'''
Event Types
1 = Create
2 = Destroy
3 = Boot
4 = Shutdown
5 = Inconsistency
'''

def add_and_commit(obj)
    db.session.add(obj)
    db.session.commit()

def shutdown_event(vmid):
    new_event = Event(4, vmid, datetime.datetime.now())
    add_and_commit(new_event)

def startup_event(vmid):
    new_event = Event(3, vmid, datetime.datetime.now())
    add_and_commit(new_event)

def create_event(vmid):
    new_event = Event(1, vmid, datetime.datetime.now())
    add_and_commit(new_event)

def destroy_event(vmid):
    new_event = Event(2, vmid, datetime.datetime.now())
    add_and_commit(new_event)

def inconsistent_event(vmid):
    new_event = Event(5, vmid, datetime.datetime.now())
    add_and_commit(new_event)

