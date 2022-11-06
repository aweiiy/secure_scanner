#!/bin/sh

#initial update and upgrade
sudo apt update
sudo apt upgrade -y
#install needed packages
sudo apt install apt-transport-https ca-certificates curl gnupg2 software-properties-common -y
#install ansible
sudo apt-get install ansible -y
#install opennebula
wget -q -O- https://downloads.opennebula.io/repo/repo.key | sudo apt-key add -
echo "deb https://downloads.opennebula.io/repo/6.4/Debian/11 stable opennebula" | sudo tee /etc/apt/sources.list.d/opennebula.list
sudo apt update
sudo apt install opennebula opennebula-sunstone opennebula-gate opennebula-flow opennebula-provision opennebula-fireedge opennebula-tools -y
#install sshpass
sudo apt-get install sshpass -y
#launch docker-compose
sudo docker-compose up -d --build
sudo docker-compose -f docker-compose.yml -f docker-compose.development.yml up --build
