wget -q -O- https://downloads.opennebula.io/repo/repo.key | sudo apt-key add -
echo "deb https://downloads.opennebula.io/repo/6.4/Debian/11 stable opennebula" | sudo tee /etc/apt/sources.list.d/opennebula.list
sudo apt update
sudo apt install vim opennebula onetemplate opennebula-tools -y
