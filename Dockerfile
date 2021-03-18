FROM tiangolo/uwsgi-nginx-flask:python3.8

EXPOSE 5000
ENV FLASK_APP=app/main.py

COPY ./app /app
COPY dependencies dependencies

RUN pip install -r /app/requirements.txt
