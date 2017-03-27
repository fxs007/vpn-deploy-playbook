#!/bin/bash

vagrant box update
vagrant destroy -f
VBoxManage dhcpserver remove --ifname vboxnet0
#VBoxManage dhcpserver add --ifname vboxnet0 --ip 192.168.56.2 --netmask 255.255.255.0 --lowerip 192.168.56.150 --upperip 192.168.56.199 --enable
vagrant up --no-provision
../generate_hosts.sh vb
vagrant provision

