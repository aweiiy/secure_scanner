# Secure Vulnerability Scanner For System Auditing

## Run instructions
(only tested on linux OS)


From the main project folder run the following command:
```sh
sudo bash run.sh
```
- After running run.sh, the script will update the machine and install docker, opennebula and other packages
- Then the script will ask for credentials for opennebula for server creation
- After that the script asks for credentials for the remote machines on open nebula
- After getting the credentials it automatically creates an .env file  with the provided details that will be used in the project.
- When the .env file is created, it will run another script that logs in to open nebula and created two virtual machines and adds their IP addresses to the ansible hosts file and generates a ansible.cfg file with the login to the machine from the provided details.
- After all is ready, the script will launch the docker-compose command where docker containers will be created, ansible will connect to the other machines and the project will be running and accessable on port 5001.


Note: You can create .env file manually by copying .env-example file and filling the data there, then run sudo bash run.sh and it will skip the crenedtial entering.


TLDR: run the command sudo bash run.sh and provide opennebula and virtual machine credentials, and the script will automatically login and create other machines.