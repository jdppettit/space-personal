#!/bin/bash

echo -e "Welcome to Space!"
echo -e "---------------------------------------------"
echo -e "This script will attempt to start and install all system services necessary to run space."
echo -n
echo -e "Updating yum db..."

echo -n
echo -e "Adding mongodb.repo to /etc/yum.repos.d"

cp /srv/space/conf.d/mongodb.repo /etc/yum.repos.d/mongodb.repo

echo -n
echo -e "Getting RPM for RabbitMQ..."

wget -O /etc/yum.repos.d/epel-erlang.repo http://repos.fedorapeople.org/repos/peter/erlang/epel-erlang.repo
yum install erlang
rpm --import http://www.rabbitmq.com/rabbitmq-signing-key-public.asc
rpm -Uvh http://www.rabbitmq.com/releases/rabbitmq-server/v3.1.4/rabbitmq-server-3.1.4-1.noarch.rpm

yum update

echo -n
echo -e "Installing mongodb-org rabbitmq-server qemu-kvm qemu-img virt-manager libvirt libvirt-python python virtinst libvirt-client virt-install virt-viewer dhcp"

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
echo -e "Starting libvirtd..."

service libvirtd start

echo -n
echo -e "Starting RabbitMQ..."

service rabbitmq-server start

echo -n
echo -e "Starting Space..."

service space start

echo -n
echo -e "Starting celery worker..."

sh /srv/space/scripts/celery.sh

echo -n
echo -e "----------------------------------------"
echo -e "All done, enjoy!"
