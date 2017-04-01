#!/bin/bash
#ansible static inventory
vagrant up --no-provision
../generate_hosts.sh do
vagrant provision
