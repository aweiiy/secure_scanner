#!/bin/sh
BASE_DIR=$(readlink -f "$(dirname "$0")")
#initial update and upgrade
sudo apt update
sudo apt upgrade -y
#install needed packages
sudo apt install apt-transport-https ca-certificates curl gnupg2 software-properties-common -y
#install docker
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose -y
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
newgrp docker
sudo apt-get install sshpass -y

echo "Docker installed."
echo "Installing opennebula."
source $BASE_DIR/scripts/opennebula.sh
echo "Opennebula installed."

source $BASE_DIR/scripts/create_vms.sh
echo "VMs created."

#launch docker-compose
sudo docker-compose up -d --build
sudo docker-compose -f docker-compose.development.yml up --build
