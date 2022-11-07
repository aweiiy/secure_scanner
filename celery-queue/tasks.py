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
    #time.sleep(5)
    ansible_playbook(website_name, report_id)
    counter = 0
    while True:
        counter += 1
        if counter == 10:
            URL = f'http://web:5001/check/{report_id}'
            r = requests.get(url=URL)
            counter = 0

        URL = f'http://web:5001/api/count_files/{report_id}'
        r = requests.get(url = URL)
        data = r.json()
        if data == 2:
            URL = f'http://web:5001/api/merge_files'
            requests.post(url = URL, data = {'report_id': report_id}, auth=HTTPBasicAuth('admin', 'admin'))
            break
        time.sleep(10)
    return 'Report generated'






def ansible_playbook(website_name: str, report_id: int) -> str:
    name = re.compile(r"https?://(www\.)?")
    name = name.sub('', website_name).strip().strip('/')
    subprocess.run([f'ansible servers -m shell -b -e ansible_sudo_pass= -a "sudo rm /tmp/nmap.txt; sudo docker run --rm -it instrumentisto/nmap -A -p 5001 -T4 {name} > /tmp/nmap.txt ; curl -u admin:admin -F "file=@/tmp/nmap.txt" http://web:5001/api/add/{report_id}"'], shell=True)

    return f"Ansible playbook executed"

#docker run --rm -it instrumentisto/nmap -A -T4 172.18.0.4
#docker run --rm -it frapsoft/nikto -host 172.18.0.4
#docker run --rm -it wpscanteam/wpscan --url 172.18.0.4 --random-user-agent --enumerate u
#docker run --rm -it hypnza/dirbuster -u 172.18.0.4


#sudo docker run --rm -it frapsoft/nikto -host {website_name} -output /tmp/{report_id}.txt > /tmp/{report_id}.txt | curl -F "file=@/tmp/{report_id}.txt" http://127.0.0.1:5001/api/add/{report_id
#sudo docker run --rm -it instrumentisto/nmap -A -p 5001 -T4 193.219.91.103 > /tmp/1.xml ; curl --data-binary "@/tmp/1.xml" http://127.0.0.1:5001/api/add/1
