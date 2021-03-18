FROM tiangolo/uwsgi-nginx-flask:python3.8

EXPOSE 5000
ENV FLASK_APP=app/main.py

COPY app/requirements.txt requirements.txt
COPY dependencies dependencies
RUN pip install -r requirements.txt

WORKDIR /app
COPY ./app .
