FROM tiangolo/uwsgi-nginx-flask:python3.8

EXPOSE 5000

COPY ./app /app

RUN pip install -r /app/requirements.txt

