FROM tiangolo/uwsgi-nginx-flask:python3.8

ENV FLASK_APP=app/main.py

COPY app/requirements.txt requirements.txt
COPY dependencies dependencies

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app app
WORKDIR /app

