FROM python:3.7.3-stretch

ENV TZ Asia/Taipei

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt


