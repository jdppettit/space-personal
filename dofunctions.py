import digitalocean
import data

def get_token():
    config = data.get_config()
    return config['do_api_key']

def get_manager():
    token = get_token()
    manager = digitalocean.Manager(token=token)
    return manager

def get_droplets():
    manager = get_manager()
    all_droplets = manager.get_all_droplets()
    return all_droplets

def get_droplet(id):
    manager = get_manager()
    droplet = manager.get_droplet(id)
    return droplet

def make_droplet(name, region, image, size):
    token = get_token()
    droplet = digitalocean.Droplet(token=token,
                                    name=name,
                                    region=region,
                                    image=image,
                                    size=size)
    droplet.create()
    droplet = get_droplet(str(droplet).split(" ")[0])
    return droplet

def destroy_droplet(id):
    manager = get_manager()
    droplet = manager.get_droplet(id)
    stat = droplet.destroy()
    if stat:
        return 1
    else:
        return 0

def shutdown_droplet(id):
    manager = get_manager()
    droplet = manager.get_droplet(id)
    droplet.shutdown()

def start_droplet(id):
    manager = get_manager()
    droplet = manager.get_droplet(id)
    droplet.power_on()

def reboot_droplet(id):
    manager = get_manager()
    droplet = manager.get_droplet(id)
    droplet.power_cycle()

def get_dist_images():
    manager = get_manager()
    dist_images = manager.get_data("https://api.digitalocean.com/v2/images?page=1&per_page=1&type=distribution")
    for image in dist_images['images']:
        if image['slug']:
            data.make_do_image(image['slug'], image['id'])

def get_sizes():
    manager = get_manager()
    sizes = manager.get_data("https://api.digitalocean.com/v2/sizes")
    for size in sizes['sizes']:
        data.make_do_size(size['slug'], size['memory'], size['vcpus'], size['disk'], size['transfer'], size['price_monthly'], size['price_hourly'])

def get_regions():
    manager = get_manager()
    regions = manager.get_data("https://api.digitalocean.com/v2/regions")
    for region in regions['regions']:
        data.make_do_region(region['slug'], region['name'])
