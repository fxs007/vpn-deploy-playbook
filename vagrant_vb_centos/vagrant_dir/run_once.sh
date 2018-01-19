#!/bin/sh
exec > "/root/$(basename ${0}).log1" 2>&1
set -x

install_locale() {
  locale-gen en_US.UTF-8
}

install_root_ssh_key() {
    mkdir -p /root/.ssh
    touch /root/.ssh/authorized_keys
    chmod 0644 /root/.ssh/authorized_keys
    echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEA1fwtpwzYdB76K4ll9m0SVnSWTZByXmrFrfvTZu2PUAcQ8nicKm5zbujozGERQ+6qM9rfRLVxLfULJ57xzKWJmmyl9o6jP/q6pXECVplscjrNDVWUxJCh+MspsiCH/uebyl6lTqENVTNuxCE4hwb03WMdoLGxCOWgEzvS4OjVozTuMaBMOgmAGP440xYT4lZtU65b29OP+PAcI2Nzr3afziwQ4MD7KSBVAg6R20eu82VAAXF2M8MXFdRxc0tPvhFHPey7rlKjLFKDy93xBvXscvhfHuKsaVZgmLftmIcwNcZ4/khSuZJkKduzmaKHqJFHoXOa7NYIP7rEIj9Bge/piw== rsa-key-20150622" >> /root/.ssh/authorized_keys
}

install_jenkins() {
    yum install -y wget java
    wget -O /etc/yum.repos.d/jenkins.repo http://pkg.jenkins-ci.org/redhat/jenkins.repo
    rpm --import https://jenkins-ci.org/redhat/jenkins-ci.org.key
    yum install -y jenkins
    sed -i 's/^JENKINS_HOME=.*$/JENKINS_HOME=\/vagrant\/jenkins/' /etc/sysconfig/jenkins
    /etc/init.d/jenkins start
}

install_vnc() {
  apt-get install -y vnc4server xvnc4viewer
}

if [ ! -f ~/runonce ]
then
  #ONCE RUN CODE HERE
  install_locale
  install_jenkins
  install_root_ssh_key
  3install_vnc
 
  touch ~/runonce
fi
