from database.db import db
from flask_user import UserMixin


# Model Entries
class Task(db.Document):
    name = db.StringField(max_length=255)
    labels = db.ListField()
    hierarchy = db.ListField()
    parent = db.ReferenceField('Task')
    interfaces = db.ListField()
    text = db.StringField()
    html = db.BooleanField()
    desc_keys = db.ListField()
    desc = None


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
    related_to = db.ReferenceField('Annotation')
    desc = None
