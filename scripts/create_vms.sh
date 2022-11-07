#!/bin/bash
set -e

CENDPOINT=https://grid5.mif.vu.lt/cloud3/RPC2
TID=1570
CPU=0.1
VCPU=3
RAM='1024m'
BASE_DIR=$(readlink -f "$(dirname "$0")")
CUSER=$(cat $BASE_DIR/../.env | grep CLOUD_USER | cut -d "=" -f2)
CPASS=$(cat $BASE_DIR/../.env | grep CLOUD_PASS | cut -d "=" -f2)
SRV_PASS=$(cat $BASE_DIR/../.env | grep SRV_PASS | cut -d "=" -f2)
SRV_1=''
SRV_2=''

# Create 2 VMs
for i in {1..2}
do
    echo "Creating VM $i"
    CVMREZ=$(onetemplate instantiate $TID --name testas --cpu $CPU  --vcpu $VCPU --memory $RAM --disk debian11:size=3000:IMAGE_UNAME=oneadmin --user $CUSER --password $CPASS --endpoint $CENDPOINT)
    CVMID=$(echo $CVMREZ |cut -d ' ' -f 3)
    echo $CVMID

    echo "Waiting for VMs to RUN: 40 sec."
    sleep 40

    onevm show $CVMID --user $CUSER --password $CPASS --endpoint $CENDPOINT >$CVMID.txt
    CSSH_CON=$(cat $CVMID.txt | grep 'CONNECT_INFO1' | cut -d '=' -f 2 | tr -d '"')
    CSSH_PRIP=$(cat $CVMID.txt | grep 'PRIVATE_IP' | cut -d '=' -f 2 | tr -d '"')

    echo "IP: $CSSH_PRIP"
    echo $CVMID >> $BASE_DIR/../vms.txt
    if [ $i -eq 1 ]
    then
        SRV_1=$CSSH_PRIP
    else
        SRV_2=$CSSH_PRIP
    fi

    ssh-keygen -f "/home/$CUSER/.ssh/known_hosts" -R $CSSH_PRIP
    ssh-keygen -f "/root/.ssh/known_hosts" -R $CSSH_PRIP
    if [ -f "/home/$CUSER/.ssh/id_rsa.pub" ]; then
        cp /home/$CUSER/.ssh/id_rsa.pub $BASE_DIR/../celery-queue/ansible/keys/id_rsa.pub
        cp /home/$CUSER/.ssh/id_rsa $BASE_DIR/../celery-queue/ansible/keys/id_rsa
        echo "Key exists."
    else
        ssh-keygen -t rsa -f "/home/$CUSER/.ssh/id_rsa" -q -N ""
        cp /home/$CUSER/.ssh/id_rsa.pub $BASE_DIR/../celery-queue/ansible/keys/id_rsa.pub
        cp /home/$CUSER/.ssh/id_rsa $BASE_DIR/../celery-queue/ansible/keys/id_rsa
        echo "Key created."
    fi

    sshpass -p $SRV_PASS ssh-copy-id -o StrictHostKeyChecking=no -i /home/$CUSER/.ssh/id_rsa.pub $CUSER@$CSSH_PRIP
done


echo "" >> $BASE_DIR/../.env
echo "SRV1_IP=$SRV_1" >> $BASE_DIR/../.env
echo "SRV2_IP=$SRV_2" >> $BASE_DIR/../.env


echo "[servers]" > hosts
echo "[server1]" >> hosts
echo "$CUSER@$SRV_1 ansible_port=22 ansible_ssh_private_key_file=/root/.ssh/id_rsa ansible_su_pass=$SRV_PASS" >> hosts
echo "[server2]" >> hosts
echo "$CUSER@$SRV_2 ansible_port=22 ansible_ssh_private_key_file=/root/.ssh/id_rsa ansible_su_pass=$SRV_PASS" >> hosts

sudo cp hosts $BASE_DIR/../celery-queue/ansible/inventory
