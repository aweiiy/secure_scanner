import os
import time
import subprocess
from celery import Celery


CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379'),
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')

celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)


@celery.task(name='tasks.add')
def add(x: int, y: int) -> int:
    time.sleep(5)
    return x + y

@celery.task(name='tasks.generate_report')
def generate_report(website_name: str) -> str:
    time.sleep(5)
    subprocess.run(['sh', 'generate_report.sh', website_name])
    return f"Report for {website_name} generated"

#docker run --rm -it instrumentisto/nmap -A -T4 172.18.0.4
#docker run --rm -it frapsoft/nikto -host 172.18.0.4
#docker run --rm -it wpscanteam/wpscan --url 172.18.0.4 --random-user-agent --enumerate u
#docker run --rm -it hypnza/dirbuster -u 172.18.0.4

#

