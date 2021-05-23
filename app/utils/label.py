from dataclasses import dataclass, asdict, field
from flask_restx import fields
import uuid
from enum import Enum


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
    linked_entry_key: str = None
    linked_entry_value: str = None


@dataclass
class IdLabel(Label):
    id_value: str = field(default_factory=uuid.uuid4)

    def __post_init__(self):
        self.id_value = str(self.id_value)


class LabelEnum(Enum):

    ANNOTATION = AnnotationLabel
    MANUAL = ManualBoolLabel
    LINKED = LinkedBoolLabel
    ID = IdLabel
