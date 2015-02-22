import data
import random

def make_api_key(length=20):
    api_key = ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPWRSTUVWXYZ') for i in range(length))
    return api_key

def set_api_key(username, key):
    data.update_admin_api(username, key)

def verify_key(key):
    results = data.get_api_key(key)
    if results.count() > 0:
        return True
    return False


