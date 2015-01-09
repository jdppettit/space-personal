from models import db, Log

def create_log(message, level):
    logm = Log(datetime.datetime.now(), message, level)
    db.session.add(logm)
    db.session.commit()
