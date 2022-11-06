#!/bin/bash
set -e

CENDPOINT=https://grid5.mif.vu.lt/cloud3/RPC2
TID=1570
CPU=0.1
VCPU=3
RAM='1024m'
CUSER=$(cat ../.env | grep CLOUD_USER | cut -d "=" -f2)
CPASS=$(cat ../.env | grep CLOUD_PASS | cut -d "=" -f2)
SRV_PASS=$(cat ../.env | grep SRV_PASS | cut -d "=" -f2)

CVMREZ=$(onetemplate instantiate $TID --name testas --cpu $CPU  --vcpu $VCPU --memory $RAM --user $CUSER --password $CPASS --endpoint $CENDPOINT)
CVMID=$(echo $CVMREZ |cut -d ' ' -f 3)
echo $CVMID

echo "Waiting for VMs to RUN: 40 sec."
sleep 40

onevm show $CVMID --user $CUSER --password $CPASS --endpoint $CENDPOINT >$CVMID.txt
CSSH_CON=$(cat $CVMID.txt | grep 'CONNECT_INFO1' | cut -d '=' -f 2 | tr -d '"')
CSSH_PRIP=$(cat $CVMID.txt | grep 'PRIVATE_IP' | cut -d '=' -f 2 | tr -d '"')
#CSSH_PORT=$(cat $CVMID.txt | grep 'TCP_PORT_FORWARDING' | cut -d '=' -f 2 | tr -d '"' | cut -d ':' -f1)
PORT=$(cat $CVMID.txt | grep 'TCP_PORT_FORWARDING' | cut -d '=' -f 2 | tr -d '"' | cut -d ':' -f 2 | cut -d ' ' -f 2 )

echo "Connection string: $CSSH_CON"
echo "IP: $CSSH_PRIP"
echo $CVMID >>../vms.txt
#echo "Port: $CSSH_PORT"


ssh-keygen -f "/home/$CUSER/.ssh/known_hosts" -R $CSSH_PRIP
ssh-keygen -f "/root/.ssh/known_hosts" -R $CSSH_PRIP
if [ -f "/home/$CUSER/.ssh/id_rsa.pub" ]; then
    echo "Key exists."
else
    ssh-keygen -t rsa -f "/home/$CUSER/.ssh/id_rsa" -q -N ""
fi

sshpass -p $SRV_PASS ssh-copy-id -o StrictHostKeyChecking=no -i /home/$CUSER/.ssh/id_rsa.pub $CUSER@$CSSH_PRIP




echo "[webserver]" > inventory
echo "$CUSER@$CSSH_PRIP ansible_port=22 ansible_ssh_private_key_file=/home/$CUSER/.ssh/id_rsa ansible_su_pass=$SRV_PASS" >> inventory

sudo cp inventory /home/edsa6402/ansible/inventory

sshpass -p $SRV_PASS ssh $CUSER@$CSSH_PRIP "mkdir -p ~/test"