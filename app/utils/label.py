from dataclasses import dataclass, asdict
from flask_restx import fields


@dataclass
class Label:
    name: str = None
    multiple: bool = False
    manual_bool: bool = False
    linked_bool: bool = False

    def to_dict(self):
        return asdict(self)

    @classmethod
    def for_marshalling(cls):
        label_obj = cls(name=fields.String, multiple=fields.Boolean,
                        manual_bool=fields.Boolean, linked_bool=fields.Boolean)
        return label_obj.to_dict()
