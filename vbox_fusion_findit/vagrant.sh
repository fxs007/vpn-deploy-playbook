#!/bin/sh
set -e

download_ova() {
  local readonly DATE=${1:-"`date +%Y%m%d`"}
  local readonly URL="http://10.74.68.44:8081/nexus/content/repositories/snapshots/OM/VM/FindITManager-1.1.0.${DATE}beta.ova"
  local readonly output=`echo ${URL} | awk 'BEGIN{FS="/"}{print $NF}'`
  if [ ! -e ${output} ]
  then
    axel -n 20 ${URL} 1>&2
    #wget ${URL} --directory-prefix=./ 1>&2
  fi
  echo ${output}
}

create_box () {
  local readonly ova_file=$1
  local readonly box_name=$2
  local readonly vm_name=$2
  VBoxManage import ${ova_file} --vsys 0 --vmname ${vm_name} --eula accept
  VBoxManage list vms --long
  VBoxManage showvminfo ${vm_name}
  VBoxManage list hdds

  VBoxManage startvm ${vm_name}
  echo "Will sleep 300"
  sleep 300
  #try proper shutdown
  VBoxManage controlvm ${vm_name} acpipowerbutton
  sleep 30
  VBoxManage controlvm ${vm_name} poweroff || true

  #package VM as a Vagrant box. Will poweroff VM if not
  vagrant package --base ${vm_name} --output ${box_name}.box
  #box file is actually a tar ball, containing vmdk, ovf and Vagrantfile
  #mv test1.box test1.box.tar.gz; tar xvf test1.box.tar.gz

  #add it to the list of your local Vagrant boxes
  vagrant box add --force ${box_name}.box --name ${box_name}

  #cleanup  
  VBoxManage unregistervm ${vm_name} --delete
  rm "${box_name}.box"

  [ -d ./vagrant_dir ] || mkdir -- ./vagrant_dir
  #http://stackoverflow.com/questions/17845637/how-to-change-vagrant-default-machine-name#20431791
  cat <<EOF >Vagrantfile
Vagrant.configure("2") do |config|
  config.vm.box = "${box_name}"
  config.ssh.insert_key = true
  config.ssh.keys_only = true
  config.ssh.username = "cisco"
  config.ssh.private_key_path = "~/.ssh/id_rsa"
  #without vm and provider define, vm name is DIRECTORY_default_TIMESTAMP
  #with only vm define, vm name is DIRECTORY_VM-DEFINE_TIMESTAMP
  config.vm.define "vm1" do |vm1|
#    vm1.vm.network "private_network", ip: "192.168.33.180"
    vm1.vm.provision "shell", inline: <<-SHELL
      sudo apt-get update
      sudo apt-get install -y tmux fakeroot expect git jq
      sudo apt-get install -y virtualbox-guest-additions-iso virtualbox-guest-utils
    SHELL
  end
  #synced dir
#  config.vm.synced_folder File.expand_path("./vagrant_dir"),
#    "/vagrant",
#    :create => true,
#    :mount_option => "dmode=755,fmode=666"

  #with provider name, vm name is PROVIDER-NAME
  config.vm.provider :virtualbox do |vb|
    vb.name = "${vm_name}"
    vb.gui = false
    vb.customize ["modifyvm", :id, "--memory", "3072"]
    vb.customize ["modifyvm", :id, "--cpus", "1"]
  end
end
EOF

  vagrant up --no-provision
}

remove_vm() {
  local readonly vm_name=$1
  vagrant destroy -f
  vagrant status
  vagrant global-status
}

remove_box() {
  local readonly box_name=$1
  rm -f "${box_name}.box" || true
  vagrant box remove "$box_name" || true
  vagrant box list
}

remove_outdated_box() {
  vagrant box list
  vagrant box prune
  vagrant box list
}

old_passwd="cisco"
new_passwd="qwer1234!"

provision0() {
    expect -c "
        spawn vagrant ssh
        set timeout 3
        expect {
                {'s password:} { send "$old_passwd"\r; exp_continue;}
                {(current) UNIX password:} { send "$old_passwd"\r; exp_continue;}
                {New password:} {send "$new_passwd"\r; exp_continue;}
                {Retype new password:} {send "$new_passwd"\r; exp_continue;}
        }
        set timeout 600
                expect eof
                exit
    "
}

provision1() {
    expect -c "
        spawn vagrant ssh
        set timeout 3
        expect {
                {'s password:} { send "$new_passwd"\r; exp_continue;}
        }
        expect {
                {findit-*:} { send {sudo sh -c 'echo \"cisco ALL=NOPASSWD:ALL\">/etc/sudoers.d/cisco'}; send \r}
        }
        expect {
                {password for cisco:} { send "$new_passwd"\r; exp_continue}
                {findit-*:} { send {sudo chmod 0440 /etc/sudoers.d/cisco}; send \r}
        }
        expect {
                {findit-*:} {send exit\r;}
        }
        set timeout 600
                expect eof
                exit
    "
}

provision2() {
    expect -c "
        spawn vagrant ssh
        set timeout 3
        expect {
                {'s password:} { send "$new_passwd"\r; exp_continue;}
        }
        expect {
                {findit-*:} { send {mkdir ~/.ssh}; send \r}
        }
        expect {
                {findit-*:} { send { echo 'ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEA1fwtpwzYdB76K4ll9m0SVnSWTZByXmrFrfvTZu2PUAcQ8nicKm5zbujozGERQ+6qM9rfRLVxLfULJ57xzKWJmmyl9o6jP/q6pXECVplscjrNDVWUxJCh+MspsiCH/uebyl6lTqENVTNuxCE4hwb03WMdoLGxCOWgEzvS4OjVozTuMaBMOgmAGP440xYT4lZtU65b29OP+PAcI2Nzr3afziwQ4MD7KSBVAg6R20eu82VAAXF2M8MXFdRxc0tPvhFHPey7rlKjLFKDy93xBvXscvhfHuKsaVZgmLftmIcwNcZ4/khSuZJkKduzmaKHqJFHoXOa7NYIP7rEIj9Bge/piw== rsa-key-20150622' > ~/.ssh/authorized_keys}; send \r}
        }
        expect {
                {findit-*:} { send { chmod 0644 ~/.ssh/authorized_keys}; send \r}
        }
        expect {
                {findit-*:} { send exit\r}
        }
        set timeout 600
                expect eof
                exit
    "
}

provision3() {
    local OPTIONS
    OPTIONS=`vagrant ssh-config | grep -v '^Host ' | awk -v ORS=' ' '{print "-o " $1 "=" $2}'`
    scp ${OPTIONS} p2.sh cisco@:/home/cisco

    expect -c "
        spawn vagrant ssh
        set timeout 60
        expect {
                {findit-*:} { send sudo /home/cisco/p2.sh\r}
        }
        expect {
                {findit-*:} { send exit\r}
        }
        set timeout 600
                expect eof
                exit
    "
}

do_provision() {
    #findit ova disabled ssh. Need to enable ssh via vty. provision0 is of no use
    #provision0
    provision1
    provision2
    provision3
    vagrant provision
    echo "provision done"
}

do_up() {
    ova_file="$(download_ova)"
    create_box ${ova_file} "$vm_name"
}

do_destroy() {
    VBoxManage controlvm "$vm_name" poweroff || true
    sleep 3
    VBoxManage unregistervm "$vm_name" --delete || true
    remove_vm "$vm_name" || true
    remove_box "$vm_name" || true
    rm Vagrantfile || true
}

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
