import pymongo 
import getpass
import uuid
import hashlib

def get_config():
    con = pymongo.MongoClient()
    db = con.space
    config_cursor = db.configuration
    config = config_cursor.find_one()
    return config

def encrypt_password(password):
    m = hashlib.sha256()
    m.update(password)
    config_rec = get_config()
    m.update(config_rec['password_salt'])
    return m.hexdigest()

def reset_password(username, password):
    con = pymongo.MongoClient()
    db = con.space
    if con:
        admin_cursor = db.admin
        admin_cursor.remove({"_id":username})
        admin_cursor.insert({"_id":username, "username":username, "password":encrypt_password(password)})
        print "Password successfully updated, you can now log in using this password.\n"
        return 0
    else:
        print "Failed to connect to database, exiting.\n"
        return 1

print "Space - Password reset v1.0\n\n"
print "This script will allow you to reset your Space login.\n"
username = raw_input("Please enter your username: ")
password = getpass.getpass("Please enter the new password: ")
password2 = getpass.getpass("Please enter the same password again: ")

if password == password2:
    reset_password(username, password)
else:
    print "Those passwords do not match, exiting."

