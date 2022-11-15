import os
import time
import subprocess
import requests
from requests.auth import HTTPBasicAuth
from celery import Celery
import re


CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379'),
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')

celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)


@celery.task(name='tasks.generate_report')
def generate_report(website_name: str, report_id: int) -> str:
    time.sleep(5)
    total_scans = int(os.environ.get('TOTAL_SCANS'))
    ansible_playbook(website_name, report_id)
    counter = 0
    while True:
        counter += 1
        if counter == 10:
            URL = f'http://web:5001/check/{report_id}'
            r = requests.get(url=URL)
            counter = 0

        URL = f'http://web:5001/api/count_files/{report_id}' #get number of files that have been uploaded by ansible hosts
        r = requests.get(url = URL)
        data = r.json()
        if data == total_scans: #check if all scans are done by checking the number of files in the report folder
            URL = f'http://web:5001/api/merge_files'
            requests.post(url = URL, data = {'report_id': report_id}, auth=HTTPBasicAuth('admin', 'admin'))
            break
        time.sleep(10)
    return 'Report generated'






def ansible_playbook(website_name: str, report_id: int) -> None:
    name = re.compile(r"https?://(www\.)?")
    name = name.sub('', website_name).strip().strip('/')

    ansible_sudo_pass = os.environ.get('SRV_PASS')
    host_url = os.environ.get('HOST_URL')

    #nmap
    subprocess.Popen([f'ansible server1 -m shell -b -e ansible_sudo_pass={ansible_sudo_pass} -a "sudo rm /tmp/nmap.txt; sudo docker run --rm -it instrumentisto/nmap -A -p 5001 -T4 {name} > /tmp/nmap.txt ; curl -u admin:admin -F "file=@/tmp/nmap.txt" {host_url}/api/add/{report_id}"'], shell=True, stdin=None, stdout=None, stderr=None)
    #nikto
    subprocess.Popen([f'ansible server2 -m shell -b -e ansible_sudo_pass={ansible_sudo_pass} -a "sudo rm /tmp/nmap.txt; sudo docker run --rm -it frapsoft/nikto -host {name} > /tmp/nikto.txt ; curl -u admin:admin -F "file=@/tmp/nikto.txt" {host_url}/api/add/{report_id}"'], shell=True, stdin=None, stdout=None, stderr=None)
    #gobuster
    subprocess.Popen([f'ansible server2 -m shell -b -e ansible_sudo_pass={ansible_sudo_pass} -a "sudo rm /tmp/dirb.txt; sudo docker run --rm -it ly4e/gobuster-docker dir -w /wordlists/common.txt -u http://{name} -z > /tmp/dirb.txt ; curl -u admin:admin -F "file=@/tmp/dirb.txt" {host_url}/api/add/{report_id}"'], shell=True, stdin=None, stdout=None, stderr=None)
    #wpscan
    subprocess.Popen([f'ansible server1 -m shell -b -e ansible_sudo_pass={ansible_sudo_pass} -a "sudo rm /tmp/wp.txt; sudo docker run --rm -it wpscanteam/wpscan --url {name} --enumerate u,p --random-user-agent > /tmp/wp.txt ; curl -u admin:admin -F "file=@/tmp/wp.txt" {host_url}/api/add/{report_id}"'], shell=True, stdin=None, stdout=None, stderr=None)


    return f"Ansible playbook executed"

#docker run --rm -it instrumentisto/nmap -A -T4 172.18.0.4
#docker run --rm -it frapsoft/nikto -host 172.18.0.4
#docker run --rm -it wpscanteam/wpscan --url 172.18.0.4 --random-user-agent --enumerate u
#docker run --rm -it hypnza/dirbuster -u 172.18.0.4


#sudo docker run --rm -it frapsoft/nikto -host {website_name} -output /tmp/{report_id}.txt > /tmp/{report_id}.txt | curl -F "file=@/tmp/{report_id}.txt" http://127.0.0.1:5001/api/add/{report_id
#sudo docker run --rm -it instrumentisto/nmap -A -p 5001 -T4 193.219.91.103 > /tmp/1.xml ; curl --data-binary "@/tmp/1.xml" http://127.0.0.1:5001/api/add/1
