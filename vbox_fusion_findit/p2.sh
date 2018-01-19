#!/bin/sh

set -x
exec > /home/cisco/log 2>&1
sleep 30

#need to manually creater sudoer
cat <<'EOF' >/etc/sudoers.d/cisco
cisco  ALL=NOPASSWD:ALL
EOF
chmod 0440 /etc/sudoers.d/cisco

systemctl start ssh
systemctl enable ssh
rm -f /etc/profile.d/autologout.sh
echo "tty2" >> /etc/securetty

apt update
apt install -y tmux wget
#apt install -y libc6-dbg
echo /var/core > /proc/sys/kernel/core_pattern
cat <<'EOF' >~/.tmux.conf
set-option -g prefix C-j
EOF

mkdir ~/.ssh || true
cat <<'EOF' >~/.ssh/authorized_keys
ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEA1fwtpwzYdB76K4ll9m0SVnSWTZByXmrFrfvTZu2PUAcQ8nicKm5zbujozGERQ+6qM9rfRLVxLfULJ57xzKWJmmyl9o6jP/q6pXECVplscjrNDVWUxJCh+MspsiCH/uebyl6lTqENVTNuxCE4hwb03WMdoLGxCOWgEzvS4OjVozTuMaBMOgmAGP440xYT4lZtU65b29OP+PAcI2Nzr3afziwQ4MD7KSBVAg6R20eu82VAAXF2M8MXFdRxc0tPvhFHPey7rlKjLFKDy93xBvXscvhfHuKsaVZgmLftmIcwNcZ4/khSuZJkKduzmaKHqJFHoXOa7NYIP7rEIj9Bge/piw== rsa-key-20150622
EOF
chmod 0644 ~/.ssh/authorized_keys

sed -i 's|root:x:0:0:root:/root:/usr/sbin/nologin|root\:x\:0\:0\:root\:/root\:/bin/bash|' /etc/passwd


