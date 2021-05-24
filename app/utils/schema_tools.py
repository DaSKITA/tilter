from config import Config
from utils.label import AnnotationLabel

def new_subtask_needed(entry):
    more_than_one_non_artificial = 1 < sum([True for field in entry.keys() if not field.startswith("_")])
    # TODO: what if element is a list?
    return more_than_one_non_artificial or any(isinstance(val, dict) for val in entry.values())

def construct_first_level_labels(as_dict: bool = None):
    labels = []

    # load tilt schema
    schema = Config.SCHEMA_DICT

    # construct first-level labels from tilt schema
    for i in schema.keys():
        try:
            label = AnnotationLabel(name=schema[i]["_desc"], multiple=False)
        except TypeError:
            label = AnnotationLabel(name=schema[i][0]["_desc"], multiple=True)
        if as_dict:
            label = label.to_dict()
        labels.append(label)

    return labels
