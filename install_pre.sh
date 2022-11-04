#!/bin/sh
sudo apt update
sudo apt upgrade -y
sudo apt install apt-transport-https ca-certificates curl gnupg2 software-properties-common -y
sudo apt-add-repository --yes --update ppa:ansible/ansible
sudo apt install ansible -y
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose -y
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
newgrp docker
sudo apt-get install git -y
git clone https://github.com/aweiiy/secure_scanner.git
cd secure_scanner
sudo docker-compose up -d --build
sudo docker-compose -f docker-compose.yml -f docker-compose.development.yml up --build


