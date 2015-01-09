from models import db, Log

import datetime

def create_log(message, level):
    logm = Log(datetime.datetime.now(), message, level)
    db.session.add(logm)
    db.session.commit()
