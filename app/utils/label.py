from dataclasses import dataclass, asdict
from flask_restx import fields
import uuid


@dataclass
class Label:
    name: str = None

    def to_dict(self):
        return asdict(self)


@dataclass
class AnnotationLabel(Label):
    multiple: bool = False

    @classmethod
    def for_marshalling(cls):
        label_obj = cls(name=fields.String, multiple=fields.Boolean)
        return label_obj.to_dict()


@dataclass
class ManualBoolLabel(Label):
    manual_bool_entry: str = None


@dataclass
class LinkedBoolLabel(Label):
    linked_entry: str = None


@dataclass
class IdLabel(Label):
    id_value: str = str(uuid.uuid4())
