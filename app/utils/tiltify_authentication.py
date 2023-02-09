import requests

from config import Config, TILTIFY


def get_tiltify_token():
    payload = {"password": Config.JWT_SECRET_KEY}
    url = f"http://{TILTIFY.address}:{TILTIFY.port}"
    return requests.post(url + '/api/auth', json=payload, headers={'Content-Type': 'application/json'}).json()
