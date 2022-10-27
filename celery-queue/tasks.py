import os
import time
import subprocess
import requests
from celery import Celery


CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379'),
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')

celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)


@celery.task(name='tasks.add')
def add(x: int, y: int) -> int:
    time.sleep(5)
    return x + y

@celery.task(name='tasks.generate_report')
def generate_report(website_name: str, report_id: int) -> str:
    time.sleep(5)
    try:
        ansible_playbook(website_name, report_id)
        while True:
            URL = f'http://127.0.0.1:5001/api/check_count/'
            data = {'report_id': report_id}
            auth = ('admin', 'admin')
            r = requests.post(url=URL, data=data, auth=auth)

            if r.text == '3':
                break
            else:
                time.sleep(1)

    except Exception as e:
        return f"Error: {e}"


def ansible_playbook(website_name: str, report_id: int) -> str:
    subprocess.run([f'docker run --rm --entrypoint sh instrumentisto/nmap -c "nmap -A -T5 -p 5001 -oX /tmp/1.xml 127.0.0.1 && curl -F "file=@/tmp/1.xml" http://127.0.0.1:5001/api/add/{report_id}"'])
    #subprocess.run(['ansible', 'srv_2', '-m', 'shell', '-a', f'sudo docker run --rm -it frapsoft/nikto -host {website_name} -output /tmp/{report_id}.txt > /tmp/{report_id}.txt | curl -F "file=@/tmp/{report_id}.txt" http://127.0.0.1:5001/api/add/{report_id}'])
    #subprocess.run(['ansible', 'srv_1', '-m', 'shell', '-a', f'sudo docker run --rm -it wpscanteam/wpscan --url {website_name} --format txt --output /tmp/{report_id}.txt > /tmp/{report_id}.txt | curl -F "file=@/tmp/{report_id}.txt" http://127.0.0.1:5001/api/add/{report_id}'])
    return f"Ansible playbook executed"

#docker run --rm -it instrumentisto/nmap -A -T4 172.18.0.4
#docker run --rm -it frapsoft/nikto -host 172.18.0.4
#docker run --rm -it wpscanteam/wpscan --url 172.18.0.4 --random-user-agent --enumerate u
#docker run --rm -it hypnza/dirbuster -u 172.18.0.4


#sudo docker run --rm -it frapsoft/nikto -host {website_name} -output /tmp/{report_id}.txt > /tmp/{report_id}.txt | curl -F "file=@/tmp/{report_id}.txt" http://127.0.0.1:5001/api/add/{report_id
#sudo docker run --rm -it instrumentisto/nmap -A -p 5001 -T4 193.219.91.103 > /tmp/1.xml ; curl --data-binary "@/tmp/1.xml" http://127.0.0.1:5001/api/add/1
