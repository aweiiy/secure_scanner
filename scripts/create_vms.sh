#!/bin/bash
set -e

CENDPOINT=https://grid5.mif.vu.lt/cloud3/RPC2
TID=1570
CPU=0.1
VCPU=3
RAM='1024m'
CUSER=$(cat ../.env | grep CLOUD_USER | cut -d "=" -f2)
CPASS=$(cat ../.env | grep CLOUD_PASS | cut -d "=" -f2)

CVMREZ=$(onetemplate instantiate $TID --name testas --cpu $CPU  --vcpu $VCPU --memory $RAM --user $CUSER --password $CPASS --endpoint $CENDPOINT)
CVMID=$(echo $CVMREZ |cut -d ' ' -f 3)
echo $CVMID

echo "Waiting for VMs to RUN: 40 sec."
sleep 40

onevm show $CVMID --user $CUSER --password $CPASS --endpoint $CENDPOINT >$CVMID.txt
CSSH_CON=$(cat $CVMID.txt | grep 'CONNECT_INFO1' | cut -d '=' -f 2 | tr -d '"')
CSSH_PRIP=$(cat $CVMID.txt | grep 'PRIVATE_IP' | cut -d '=' -f 2 | tr -d '"')
CSSH_PORT=$(cat $CVMID.txt | grep 'TCP_PORT_FORWARDING' | cut -d '=' -f 2 | tr -d '"' | cut -d ':' -f1)
PORT=$(cat $CVMID.txt | grep 'TCP_PORT_FORWARDING' | cut -d '=' -f 2 | tr -d '"' | cut -d ':' -f 2 | cut -d ' ' -f 2 )

echo "Connection string: $CSSH_CON"
echo "IP: $CSSH_PRIP"
echo "Port: $CSSH_PORT"

echo "[webserver]" > hosts
echo "$CUSER@$CSSH_PRIP ansible_port=$CSSH_PORT" >> hosts

ssh -f -p 22 $CUSER@$CSSH_PRIP "mkdir -p ~/test"