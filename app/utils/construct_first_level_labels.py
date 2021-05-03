from config import Config
from utils.label import Label


def construct_first_level_labels(as_dict: bool = None):
    labels = []

    # load tilt schema
    schema = Config.SCHEMA_DICT

    # construct first-level labels from tilt schema
    for i in schema.keys():
        try:
            label = Label(name=schema[i]["desc"], multiple=True)
        except TypeError:
            label = Label(name=schema[i][0]["desc"], multiple=False)
        if as_dict:
            label = label.to_dict()
        labels.append(label)

    return labels
