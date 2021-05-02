from config import Config

def construct_first_level_labels():
    labels = []

    # load tilt schema
    schema = Config.SCHEMA_DICT.copy()

    # construct first-level labels from tilt schema
    for i in schema.keys():
        try:
            labels.append((schema[i]["desc"], True))
        except:
            labels.append((schema[i][0]["desc"], False))

    return labels