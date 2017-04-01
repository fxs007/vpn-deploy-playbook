#!/bin/sh
exec > "/root/$(basename ${0}).log1" 2>&1
set -x

install_locale() {
  sudo locale-gen en_US.UTF-8
}

install_root_ssh_key() {
    mkdir -p /root/.ssh
    touch /root/.ssh/authorized_keys
    chmod 0644 /root/.ssh/authorized_keys
    echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEA1fwtpwzYdB76K4ll9m0SVnSWTZByXmrFrfvTZu2PUAcQ8nicKm5zbujozGERQ+6qM9rfRLVxLfULJ57xzKWJmmyl9o6jP/q6pXECVplscjrNDVWUxJCh+MspsiCH/uebyl6lTqENVTNuxCE4hwb03WMdoLGxCOWgEzvS4OjVozTuMaBMOgmAGP440xYT4lZtU65b29OP+PAcI2Nzr3afziwQ4MD7KSBVAg6R20eu82VAAXF2M8MXFdRxc0tPvhFHPey7rlKjLFKDy93xBvXscvhfHuKsaVZgmLftmIcwNcZ4/khSuZJkKduzmaKHqJFHoXOa7NYIP7rEIj9Bge/piw== rsa-key-20150622" >> /root/.ssh/authorized_keys
}

install_jenkins() {
    wget -q -O - https://pkg.jenkins.io/debian/jenkins-ci.org.key | apt-key add -
    sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
    apt-get install -y jenkins
    #/etc/init.d/jenkins start
}

install_vnc() {
  sudo apt-get install -y vnc4server xvnc4viewer
}

if [ ! -f ~/runonce ]
then
  #ONCE RUN CODE HERE
  install_locale
  install_jenkins
  install_root_ssh_key
  install_vnc
 
  touch ~/runonce
fi
