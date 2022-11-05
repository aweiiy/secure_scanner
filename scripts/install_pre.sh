#!/bin/sh

#initial update and upgrade
sudo apt update
sudo apt upgrade -y
#install needed packages
sudo apt install apt-transport-https ca-certificates curl gnupg2 software-properties-common -y
#install ansible
sudo apt-get install ansible -y
#install docker and opennebula
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list
wget -q -O- https://downloads.opennebula.io/repo/repo.key | sudo apt-key add -
echo "deb https://downloads.opennebula.io/repo/6.4/Debian/11 stable opennebula" | sudo tee /etc/apt/sources.list.d/opennebula.list
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose -y
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
newgrp docker
sudo apt install opennebula opennebula-sunstone opennebula-gate opennebula-flow opennebula-provision opennebula-fireedge opennebula-tools -y
#install git
sudo apt-get install git -y
#install sshpass
sudo apt-get install sshpass -y
#download project
git clone https://github.com/aweiiy/secure_scanner.git
cd secure_scanner
#launch docker-compose
sudo docker-compose up -d --build
sudo docker-compose -f docker-compose.yml -f docker-compose.development.yml up --build
