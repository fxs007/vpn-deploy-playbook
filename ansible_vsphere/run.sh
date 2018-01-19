#!/bin/sh

main()
{
  for i in $(seq 1 1)
  do
    local g ip
    g="vm-$i"
    ip="10.74.68.13$i"
    if [ "$1" = "up" ];then
      ansible-playbook ./create.yml --extra-vars "guest=$g" -vvv
      PYTHONPATH=./tools python ./tools/cli/set_vm_ip.py 10.74.68.16 administrator@vsphere.local 'Cisco123!' "$g" "$ip" 64.104.123.144
    elif [ "$1" = "provision" ];then
      PYTHONPATH=./tools python ./tools/cli/set_vm_ip.py 10.74.68.16 administrator@vsphere.local 'Cisco123!' "$g" "$ip" 64.104.123.144
    elif [ "$1" = "destroy" ];then
      ansible-playbook ./destroy.yml --extra-vars "guest=$g" -vvv
    elif [ "$1" = "ssh" ]; then
       ssh kube@"$ip"
    fi
  done
}

main $@
