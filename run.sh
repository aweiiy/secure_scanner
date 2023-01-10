#!/bin/bash
#use this script to run the project by running sudo bash run.sh
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
echo "Installing opennebula."
. $BASE_DIR/scripts/opennebula.sh
echo "Opennebula installed."

if [ -f "$BASE_DIR/.env" ]; then
    echo "File exists."
else
    #fill env variables with user input
    echo "Please enter the username for Opennebula:"
    read CLOUD_USER
    echo "Please enter the password for Opennebula:"
    stty -echo
    read CLOUD_PASS
    stty echo
    echo "Please enter the username for the virtual machines in opennebula:"
    read SRV_USER
    echo "Please enter the password for the virtual machines in opennebula:"
    stty -echo
    read SRV_PASS
    stty echo


    #create .env file
    echo "Creating .env file."
    echo "SRV_USER=$SRV_USER" > .env
    echo "SRV_PASS=$SRV_PASS" >> .env
    echo "CLOUD_USER=$CLOUD_USER" >> .env
    echo "CLOUD_PASS=$CLOUD_PASS" >> .env
    echo "TOTAL_SCANS=4" >> .env
fi



. $BASE_DIR/scripts/create_vms.sh
echo "VMs created."

#launch docker-compose
sudo docker-compose -f docker-compose.yml up --build
