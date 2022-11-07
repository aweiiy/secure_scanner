FROM ubuntu

ENV DEBIAN_FRONTEND=noninteractive
#ENV HOST 0.0.0.0

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
    apt install sshpass -y;

RUN mkdir /root/.ssh
RUN chmod 700 /root/.ssh && chown root:root /root/.ssh
WORKDIR /root/.ssh
ADD ansible/keys/id_rsa .
RUN chmod 600 id_rsa && chown root:root id_rsa
ADD ansible/keys/id_rsa.pub .
RUN chmod 644 id_rsa.pub && chown root:root id_rsa.pub
WORKDIR /
EXPOSE 22

RUN mkdir -p /etc/ansible
WORKDIR /etc/ansible
ADD ansible/cfg/ansible.cfg .
RUN chmod 644 ansible.cfg && chown root:root ansible.cfg
ADD ansible/inventory/hosts .
RUN chmod 644 hosts && chown root:root hosts
WORKDIR /


#RUN sshpass -p ${SRV_PASS} ssh-copy-id -o StrictHostKeyChecking=no ${SRV_USER}@${SRV1_IP}
#RUN sshpass -p ${SRV_PASS} ssh-copy-id -o StrictHostKeyChecking=no ${SRV_USER}@${SRV2_IP}


ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true

COPY . /queue
WORKDIR /queue

RUN pip install -U setuptools pip
RUN pip install -r requirements.txt

