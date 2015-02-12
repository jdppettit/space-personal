import data
import subprocess

def check_services():
    services = data.get_all_service()
    command = "ps aux"
    ps = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = ps.stdout.read()
    print output
    ps.stdout.close()
    ps.wait()
    for service in services:
        if service['_id'] in output and service['status'] == 0:
            data.set_service_status(service['_id'], 1)
        elif service['_id'] not in output and service['status'] == 1:
            data.set_service_status(service['_id'], 0)

def make_services():
    config = data.get_config()
    data.make_service(config['dhcp_service'], 0)
    data.make_service("celery", 0)
    data.make_service("gunicorn", 0)
    data.make_service("rabbitmq-server", 0)
    data.make_service("mongod", 0)
    check_services()
