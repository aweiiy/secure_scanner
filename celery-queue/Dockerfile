FROM ubuntu

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y gcc python2-dev libkrb5-dev && \
    apt-get install software-properties-common -y && \
    apt-get install python3-pip -y && \
    pip3 install --upgrade pip && \
    pip3 install --upgrade virtualenv && \
    pip3 install pywinrm && \
    pip3 install kerberos && \
    apt install krb5-user -y && \
    pip3 install ansible && \
    apt install openssh-server openssh-client -y && \
    apt install sshpass -y

ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true

COPY . /queue
WORKDIR /queue

RUN pip install -U setuptools pip
RUN pip install -r requirements.txt

