import digitalocean
import data

def get_token():
    config = data.get_config()
    return config['do_api_key']

def get_droplets():
    token = get_token()

