#!/bin/bash
# --------------------------------------------------------------
#https://github.com/snowch/carbon-products-development-environment/blob/master/scripts/add_new_disk.sh
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# --------------------------------------------------------------

set -e
set -x

if [ -f /etc/stratos_dev_env_disk_added_date ]
then
   echo "Stratos runtime already provisioned so exiting."
   exit 0
fi


sudo fdisk -u /dev/sdb <<EOF
n
p
1


w
EOF

#pvcreate /dev/sdb1
#vgextend VolGroup /dev/sdb1
#lvextend -L +100G /dev/VolGroup/lv_root # TODO the size needs to be passed in as a argument
#resize2fs /dev/VolGroup/lv_root

#https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/Logical_Volume_Manager_Administration/LVM_examples.html
sudo apt install -y lvm2
sudo pvcreate /dev/sdb1
sudo vgcreate VolGroup /dev/sdb1
sudo lvcreate -L 100G -n lv_root VolGroup
sudo mkfs.ext4 /dev/VolGroup/lv_root
sudo mount /dev/VolGroup/lv_root /opt

#update fstab

date > /etc/stratos_dev_env_disk_added_date
