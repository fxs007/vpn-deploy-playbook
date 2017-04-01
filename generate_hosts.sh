#!/bin/bash
#it is used to generate ansible_hosts. Can be replaced by dynamic inventory
echo "Enter $0"
#input
provisioner=$1
hosts_file="ansible_hosts"
do_token="064a853a0b2210e2f0663c38e3f8b28f2e7df8fc5e4f8caa35d8eb5c8cf34cff"
vm_ip=

#get env
if [ -z "${1+x}" ]; then #Use Alternate Value
  echo "Usage:
    ${0} do
    ${0} aws
    ${0} vb"
elif [ "do" = ${provisioner} ]; then
  #vm_ip=$(curl --stderr /dev/null -X GET -H "Content-Type: application/json" -H "Authorization: Bearer ${do_token}" "https://api.digitalocean.com/v2/droplets?tag_name=default" | jq '.droplets[].networks.v4[].ip_address' | sed -e 's/"//g')
  vm_ip=$(curl --stderr /dev/null -X GET -H "Content-Type: application/json" -H "Authorization: Bearer ${do_token}" "https://api.digitalocean.com/v2/droplets?page=1&per_page=1" | jq '.droplets[].networks.v4[].ip_address' | sed -e 's/"//g')
elif [ "aws" = ${provisioner} ]; then
  vm_ip=
elif [ "vb" = ${provisioner} ]; then
  vm_ip="192.168.33.20"
else
  echo "not supported provisioner!"
  exit 1
fi

#print env
echo "provisioner: ${provisioner}"
echo "hosts_file: ${hosts_file}"
echo "do_token: ${do_token}"
echo "vm_ip: ${vm_ip}"

#processing
echo >${hosts_file}

echo "${vm_ip} ansible_ssh_private_key_file=~/.ssh/id_rsa ansible_user=vagrant ansible_distribution=${ansible_distribution:-Ubuntu} 

[l2tp-eth-client]
${vm_ip}

[l2tp-eth-server]
${vm_ip}

[l2tp]
${vm_ip}

[pptp]
${vm_ip}

[ipsec]
${vm_ip}

[openconnect]
${vm_ip}

[vpn]
${vm_ip}

[chinadns]
${vm_ip}

[auth]
${vm_ip}

[dev]
${vm_ip}">>${hosts_file}

echo "Leave $0"
