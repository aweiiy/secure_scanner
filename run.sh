#!/bin/sh
#get the current script directory
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
echo "exit" | newgrp docker
sudo apt-get install sshpass -y

echo "Docker installed."
echo "Installing opennebula."#TODO: add base_dir to the script
. $BASE_DIR/scripts/opennebula.sh
echo "Opennebula installed."

#fill env variables with user input
echo "Please enter the username for the servers:"
read SRV_USER
echo "Please enter the password for the servers:"
read SRV_PASS
echo "Please enter the username for Opennebula:"
read CLOUD_USER
echo "Please enter the password for Opennebula:"
read CLOUD_PASS

#create .env file
echo "Creating .env file."
echo "SRV_USER=$SRV_USER" > .env
echo "SRV_PASS=$SRV_PASS" >> .env
echo "CLOUD_USER=$CLOUD_USER" >> .env
echo "CLOUD_PASS=$CLOUD_PASS" >> .env





. $BASE_DIR/scripts/create_vms.sh
echo "VMs created."

#launch docker-compose
sudo docker-compose -f docker-compose.development.yml up --build
