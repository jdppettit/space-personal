#!/bin/bash

echo -e "Welcome to Space!"
echo -e "---------------------------------------------"
echo -e "This script will attempt to start and install all system services necessary to run space."
echo -n
echo -e "Updating yum db..."

yum update

echo -n
echo -e "Installing mongodb-server rabbitmq-server qemu-kvm qemu-img virt-manager libvirt libvirt-python python virtinst libvirt-client virt-install virt-viewer dhcp"

for package in mongodb-server rabbitmq-server qemu-kvm qemu-img virt-manager libvirt libvirt-python python virtinst libvirt-client virt-install virt-viewer dhcp python-pip
do

echo -n
echo -e "Processing ${package}..."

yum install $package

echo -n
echo -e "Done."

done

echo -n
echo -e "Creating symlink for init.d file..."

ln -s /srv/space/scripts/space.sh /etc/init.d/space

echo -n
echo -e "Done."

echo -n
echo -e "Installing python requirements from requirements.txt..."

pip install -r /srv/space/requirements.txt

echo -n
echo -e "Done."

echo -n
echo -e "Finished installing packages..."

echo -n
echo -e "Starting rabbitmq..."

service rabbitmq-server start

echo -n
echo -e "Starting DHCPD..."

service dhcpd start

echo -n 
echo -e "Starting MongoDB..."

service mongod start

echo -n
echo -e "Starting Space..."

echo -n
echo -e "Starting celery worker..."

sh /srv/space/scripts/celery.sh

service space start

echo -n
echo -e "----------------------------------------"
echo -e "All done, enjoy!"
