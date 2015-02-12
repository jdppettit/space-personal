import data
import linode
import time

def get_api():
    config = data.get_config()
    api = linode.Api(config['linode_api_key'])
    return api

def get_linode(linodeID):
    api = get_api()
    linode = api.linode.list(LinodeID=linodeID)
    return linode[0]

def get_linode_ip(linodeID):
    api = get_api()
    linode_ip = api.linode.ip.list(LinodeID=linodeID)
    return linode_ip[0]

def get_datacenters():
    api = get_api()
    facilities = api.avail.datacenters()
    for facility in facilities:
        data.make_linode_facility(facility['DATACENTERID'], facility['LOCATION'])

def get_plans():
    api = get_api()
    plans = api.avail.linodeplans()
    for plan in plans:
        data.make_linode_plan(plan['PLANID'], plan['RAM'], plan['DISK'], plan['CORES'], plan['XFER'], plan['LABEL'], plan['PRICE'], plan['HOURLY'])

def get_kernels():
    api = get_api()
    kernels = api.avail.kernels()
    for kernel in kernels:
        data.make_linode_kernel(kernel['KERNELID'], kernel['LABEL'])

def get_distributions():
    api = get_api()
    distributions = api.avail.distributions()
    for dist in distributions:
        data.make_linode_distribution(dist['DISTRIBUTIONID'], dist['LABEL'])

def make_linode(datacenterID, planID):
    api = get_api()
    linode = api.linode.create(DatacenterID=datacenterID, PlanID=planID)
    return linode['LinodeID']

def make_config(linodeID, kernelID, label, diskID):
    api = get_api()
    config = api.linode.config.create(LinodeID=linodeID, KernelID=kernelID, Label=label, DiskList="%s" % str(diskID))

def make_disk(linodeID, distributionID, label, size, rootPass):
    api = get_api()
    disk = api.linode.disk.createfromdistribution(LinodeID=linodeID, DistributionID=distributionID, Label=label, Size=size, rootPass=rootPass)
    return disk['DiskID']

def boot_linode(linodeID):
    api = get_api()
    api.linode.boot(LinodeID=linodeID)

def shutdown_linode(linodeID):
    api = get_api()
    api.linode.shutdown(LinodeID=linodeID)

def reboot_linode(linodeID):
    api = get_api()
    api.linode.reboot(LinodeID=linodeID)

def delete_linode(LinodeID):
    api = get_api()
    api.linode.delete(LinodeID=linodeID)

def resize_linode(LinodeID, PlanID):
    api = get_api()
    try:
        api.linode.resize(LinodeID=LinodeID, PlanID=PlanID)
    except:
        pass

