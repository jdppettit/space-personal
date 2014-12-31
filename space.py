from flask import *
from flask.ext.sqlalchemy import SQLAlchemy

from config import *

app = Flask(__name__)

connectionString = "mysql+mysqlconnector://%s:%s@%s:3306/%s" % (username, password, hostname, database)
app.config['SQLALCHEMY_DATABASE_URI'] = connectionString
db = SQLAlchemy(app)

class Server(db.Model):
    __tablename__ = "server"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    disk_size = db.Column(db.Integer)
    disk_path = db.Column(db.String(100))
    ram = db.Column(db.Integer)
    state = db.Column(db.Integer)

    def __init__(self, name, disk_size, disk_path, ram, state):
        self.name = name
        self.disk_size = disk_size
        self.disk_path = disk_path
        self.ram = ram
        self.state = state

db.create_all()
db.session.commit()
