from dataclasses import dataclass, asdict, field
from flask_restx import fields
import uuid
from enum import Enum
from typing import Dict


@dataclass
class Label:
    name: str = None
    tilt_key: str = None

    def to_dict(self):
        label_dict = asdict(self)
        label_dict["label_class"] = self.__class__.__name__
        return label_dict


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


class LabelStrEnum(Enum):
    ANNOTATION = "AnnotationLabel"
    MANUAL = "ManualBoolLabel"
    LINKED = "LinkedBoolLabel"
    ID = "IdLabel"
    LABEL = "Label"


class LabelFactory:

    def __init__(self) -> None:
        """
        Simple Factory Class that maps incomming arguments to a specific label class.
        """
        self.label_mappings = {
            LabelStrEnum.ANNOTATION: AnnotationLabel,
            LabelStrEnum.MANUAL: ManualBoolLabel,
            LabelStrEnum.LINKED: LinkedBoolLabel,
            LabelStrEnum.ID: IdLabel,
            LabelStrEnum.LABEL: Label
        }

    def create_label(self, args_dict: Dict) -> Label:
        label_class_enum = LabelStrEnum(args_dict.pop("label_class"))
        label_class = self.label_mappings[label_class_enum]
        return label_class(**args_dict)


if __name__ == "__main__":

    label = AnnotationLabel(name="test", tilt_key="test2", multiple=False)
    print(label.to_dict())
    label = label.to_dict()
    label_factory = LabelFactory()
    label = label_factory.create_label(label)
    print(label)
