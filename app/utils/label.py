from dataclasses import dataclass, asdict


@dataclass
class Label:
    name: str
    multiple: bool = False
    manual_bool: bool = False
    linked_bool: bool = False

    def to_dict(self):
        return asdict(self)
