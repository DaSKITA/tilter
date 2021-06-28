FROM tiangolo/uwsgi-nginx-flask:python3.8

ENV FLASK_APP=app/main.py
ENV DEPLOYMENT=1

WORKDIR /app
COPY uwsgi.ini .
COPY app/requirements.txt requirements.txt
COPY dependencies dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY data data
COPY app app

CMD [ "python3", "app/main.py" ]
