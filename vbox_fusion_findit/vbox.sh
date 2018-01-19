#!/bin/sh
set -e

#search and replace:
#URL, ova_file
#user and IP is vbox_provision

download_ova() {
  if [ ! -e "$1" ]
  then
    local URL
    URL="http://10.74.68.44:8081/nexus/content/repositories/snapshots/OM/VM/$1"
    wget "${URL}" --show-progress --directory-prefix=./ 
  fi
}

vbox_delete() {
  local vm_name
  vm_name="$1"
  VBoxManage controlvm "$vm_name" poweroff || true
  sleep 1
  VBoxManage unregistervm "$vm_name" --delete || true
}

vbox_import() {
  local ova_file vm_name
  ova_file="$1"
  vm_name="$2"
  VBoxManage import "${ova_file}" --vsys 0 --vmname "${vm_name}" --eula accept
  VBoxManage list vms --long
  VBoxManage showvminfo "${vm_name}"
  VBoxManage list hdds

  VBoxManage startvm "${vm_name}"
}

vbox_provision() {
    #use dry-run if you only want to display public key
    ssh-copy-id -n user1@192.168.220.247
    .
}

do_up()
{
  vbox_import "$ova_file" "$vm_name"

}

do_destroy()
{
  vbox_delete "$vm_name"

}

do_provision()
{
  vbox_provision
}

DATE="$(date +%Y%m%d)"
ova_file="fff-image-${DATE}.ova"
vm_name=test1


case $1 in
  up)
    do_up
    ;;
  destroy)
    do_destroy
    ;;
  provision)
    do_provision
    ;;
  *)
    echo "usage: $0 up|destroy|provision"
    ;;
esac



