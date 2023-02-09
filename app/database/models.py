import requests
from datetime import datetime

from database.db import db
from flask_user import UserMixin

from config import Config, TILTIFY
from utils.tiltify_authentication import get_tiltify_token


# Model Entries
class Task(db.Document):
    name = db.StringField(max_length=255)
    labels = db.ListField(db.DictField())
    hierarchy = db.ListField()
    parent = db.ReferenceField('Task')
    interfaces = db.ListField()
    text = db.StringField()
    html = db.BooleanField(default=False, required=False)
    manual_labels = db.ListField(db.DictField(), required=False)


class User(db.Document, UserMixin):
    active = db.BooleanField(default=True)

    # User authentication information
    username = db.StringField(default='', max_length=16)
    password = db.StringField(min_length=6)

    # User information
    first_name = db.StringField(default='', max_length=255)
    last_name = db.StringField(default='', max_length=255)

    # Relationships
    roles = db.ListField(db.StringField(), default=[])


class Annotation(db.Document):
    start = db.IntField(required=True)
    end = db.IntField(required=True)
    text = db.StringField(required=True)
    label = db.StringField(required=True)
    task = db.ReferenceField('Task', required=True)
    parent_annotation = db.ReferenceField('Annotation', required=False, default=None)
    child_annotation = db.ReferenceField('Annotation', required=False, default=None)

    def save(self, *args, **kwargs):
        super(Annotation, self).save(args, kwargs)
        tiltify_token = get_tiltify_token()
        url = f"http://{TILTIFY.address}:{TILTIFY.port}"
        payload = {'documents': [{'document_name': self.task.name,
                                  'text': self.task.text}],
                   'labels': [self.label]}
        requests.post(url + "/api/train", json=payload, timeout=3000,
                      headers={'Authorization': tiltify_token, 'Content-Type': 'application/json'})


class MetaTask(db.Document):
    _id = db.StringField(required=True)
    name = db.StringField(required=True)
    created = db.StringField(required=True)
    modified = db.StringField(required=True)
    version = db.IntField(required=True)
    language = db.StringField(required=True)
    status = db.StringField(required=True)
    url = db.StringField(required=True)
    root_task = db.ReferenceField('Task', required=True)
    _hash = db.StringField(required=False)


class HiddenAnnotation(db.Document):
    """An ID in the tilt.

    Args:
        db ([type]): [description]
    """

    value = db.StringField(required=True)
    label = db.StringField(required=True)
    task = db.ReferenceField('Task', required=True)


class LinkedAnnotation(db.Document):
    """Annotations that fill out automatically, when a label to a related annotation is given.

    Args:
        db ([type]): [description]
    """
    task = db.ReferenceField('Task', required=True)
    value = db.BooleanField(required=False)
    label = db.StringField(required=True)
    related_to = db.ReferenceField('Annotation')
    manual = db.BooleanField(required=True)


class TrainingTimestamp(db.Document):
    """Simple timestamp object to schedule training calls to tiltify"""
    timestamp = db.DateTimeField(required=True)
