import data
import linode

def get_api():
    config = data.get_config()
    api = linode.Api(config['linode_api_key'])
    return api

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
    return linode['DATA']['LinodeID']

def make_config(linodeID, kernelID, label):
    api = get_api()
    config = api.linode.config.create(LinodeID=linodeID, KernelID=kernelID, Label=label)

def make_disk(linodeID, distributionID, label, size, rootPass):
    api = get_api()
    disk = api.linode.createfromdistribution(LinodeID=linodeID, DistributionID=distributionID, Label=label, Size=size, rootPass=rootPass)

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


