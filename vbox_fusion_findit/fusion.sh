#!/bin/sh
set -e

#search and replace:
#URL, ova_file
#user and password is vmware_provision

alias ovftool='/Applications/VMware\ Fusion.app/Contents/Library/VMware\ OVF\ Tool/ovftool'
alias vmrun='/Applications/VMware\ Fusion.app/Contents/Library/vmrun'

download_ova() {
  if [ ! -e "$1" ]
  then
    local URL
    URL="http://10.74.68.44:8081/nexus/content/repositories/snapshots/OM/provision/$1"
    wget "${URL}" --show-progress --directory-prefix=./ 
  fi
}

vmware_delete() {
    vmx_file=$1
    if [ -e "$vmx_file" ]
    then
        vmrun stop "$vmx_file" || true
        vmrun deleteVM "$vmx_file"
    fi
}

vmware_import() {
    ova_file="$1"
    vmx_file="$2"
    ovftool --acceptAllEulas "$ova_file" #display information
    mkdir -p "$(dirname "$vmx_file")"
    ovftool --acceptAllEulas "$ova_file" "$vmx_file"
    vmrun start "$vmx_file" nogui
    vmrun list
}

#after user initial login; sudoers#
vmware_provision() {
    #vmrun -gu 'user1' -gp 'qwe1234!' listProcessesInGuest "$vmx_file"
    vmrun -gu 'user1' -gp 'qwer1234!' CopyFileFromHostToGuest "$vmx_file" ./p2.sh /home/cisco/p2.sh
    #vmrun -gu 'user1' -gp 'qwe1234!' runScriptInGuest "$vmx_file" /bin/sh /home/cisco/p2.sh
    vmrun -gu 'user1' -gp 'qwer1234!' runProgramInGuest "$vmx_file" /usr/bin/sudo /bin/sh /home/cisco/p2.sh
    .
}

do_up()
{

  if [ -e "$vmx_file" ]
  then
    true
  else
    download_ova "$ova_file"
    vmware_import "$ova_file" "$vmx_file"
    fi
  grep en0 "$(dirname "$vmx_file")/vmware.log"
}

do_destroy()
{
  vmware_delete "$vmx_file"
}

do_provision()
{
  vmware_provision
}

DATE="$(date +%Y%m%d)"
ova_file="fff-image-${DATE}.ova"
vmx_file='./vm_dir/test1.vmx'

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



