#!/bin/bash

vagrant up --no-provision
../generate_hosts.sh do
vagrant provision
