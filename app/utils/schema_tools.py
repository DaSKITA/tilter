from config import Config
from utils.label import AnnotationLabel


def construct_first_level_labels(as_dict: bool = None):
    labels = []

    # load tilt schema
    schema = Config.SCHEMA_DICT

    # construct first-level labels from tilt schema
    for i in schema.keys():
        try:
            label = AnnotationLabel(name=schema[i]["_desc"], multiple=False, tilt_key=i)
        except TypeError:
            label = AnnotationLabel(name=schema[i][0]["_desc"], multiple=True, tilt_key=i)
        if as_dict:
            label = label.to_dict()
        labels.append(label)

    return labels


def retrieve_schema_level(hierarchy):
    schema = Config.SCHEMA_DICT.copy()
    for path_entry in hierarchy:
        try:
            schema = schema[path_entry]
        except TypeError:
            schema = schema[0][path_entry]
    if isinstance(schema, list):
        schema = schema[0]
    return schema


def get_manual_bools(hierarchy):
    schema = retrieve_schema_level(hierarchy)
    return [(k, v) for (k, v) in schema.items() if k[0] == '~' and v[0] != '#']

