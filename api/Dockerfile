FROM python:3.9-alpine

ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true
ENV PYTHONUNBUFFERED 1

ENV HOST 0.0.0.0
ENV PORT 5001
ENV DEBUG true

COPY . /api
WORKDIR /api

RUN pip install -U setuptools pip
RUN pip install -r requirements.txt

EXPOSE 5001

RUN pip install gunicorn
RUN pip3 install flask_sqlalchemy

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "3", "main:app"]
