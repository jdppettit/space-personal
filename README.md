# Space - Personal

Space is a simple virtualization control panel written in Python with Flask. Space utilizes the libvirt API to interact directly with the hypervisor, and thus (will eventually) support all virtualization technology that libvirt supports.

This project is still in a relatively early stage of development, it is feature complete but there is still a fair amount of work to be done. With that being said, use at your own risk! 

## Requirements

* Centos 6 (more support coming)
* Python2
* MongoDB
* KVM (currently only support virtualization technology)
* RabbitMQ (used by Celery)
* Variety of python packages shown [here](https://github.com/silverp1/space-personal/blob/master/requirements.txt)

## Installation

1. Clone repo in `/srv`.
2. Configure `virbr0` as bridge interface.
3. `./srv/space/scripts/setup.sh` - This will install all dependencies, start necessary services and start Space.
4. Navigate to `your.ip.address.here/setup` to complete the setup process.
5. Login and enjoy. 

## Use

* You'll want to add some IP addresses before adding a server - to do this, visit `/ip` or click networking. Its easiest to add a whole range.
* Be sure to add some images (ISOs) for your servers. You can upload them to `/var/images` if you used the default path. When you're done, you can use the import images option under `Utilities` or visit `/utils/import_images`.
* If you derped on any configuration settings you can fix it on the `Host` page at `/host`.
* You should be all set to make a new server now. 

## Notes & Misc. 

* The password for the console will not be shown when you type (or paste), this is expected, it will still work. 
* If you are brave and try this and things break, please let me know so I can fix them :) 


