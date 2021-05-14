from config import Config
from database.models import Task, Annotation, MetaTask
from mongoengine import DoesNotExist
from tilt_resources.meta import Meta


def iterate_through_hierarchy_level(parent_task, hierarchy):
    local_schema = Config.SCHEMA_DICT.copy()
    label_limited = True

    # walk through schema using hierarchy
    for i in hierarchy:
        try:
            local_schema = local_schema[i]
        except:
            local_schema = local_schema[0][i]

    # if schema is of type list change cardinality and
    if type(local_schema) is list:
        local_schema = local_schema[0]
        label_limited = False

    tasks = Task.objects(parent=parent_task, hierarchy=hierarchy)

    # there is no limitation regarding cardinality
    if not label_limited:
        tilt_value = []
        if tasks:
            for task in tasks:
                tilt_value_part = {}
                # iterate through current schema hierarchy
                for key, val in local_schema.items():
                    if type(val) in [dict, list]:
                        new_hierarchy = hierarchy.copy()
                        new_hierarchy.append(key)
                        tilt_value_part[key] = iterate_through_hierarchy_level(task, new_hierarchy)
                    elif key in ['desc', 'key']:
                        continue
                    else:
                        try:
                            tilt_value_part[key] = Annotation.objects.get(task=task, label=val).text
                        except DoesNotExist:
                            tilt_value_part[key] = None
                        except:
                            tilt_value_part[key] = Annotation.objects.get(task=task, label=val[0]).text
                tilt_value.append(tilt_value_part)
        elif type(local_schema) is dict:
            # iterate through current schema hierarchy
            tilt_value_part = {}
            for key, val in local_schema.items():
                annotations = Annotation.objects(task=parent_task, label=local_schema["desc"])
                if key in ['desc', 'key']:
                    continue
                annotations_list = [anno.text for anno in annotations]
                tilt_value_part[key] = annotations_list
            tilt_value.append(tilt_value_part)
        else:
            annotations = Annotation.objects(task=parent_task, label=local_schema)
            tilt_value = [anno.text for anno in annotations]

    # there is a limitation regarding cardinality
    else:
        tilt_value = {}
        child_task = tasks.first()
        for key, val in local_schema.items():
            if type(val) in [dict, list]:
                new_hierarchy = hierarchy.copy()
                new_hierarchy.append(key)
                tilt_value[key] = iterate_through_hierarchy_level(child_task, new_hierarchy)
            elif key in ['desc', 'key']:
                continue
            else:
                try:
                    tilt_value[key] = Annotation.objects.get(task=child_task, label=val).text
                except DoesNotExist:
                    try:
                        tilt_value[key] = Annotation.objects.get(task=parent_task, label=local_schema["desc"]).text
                    except DoesNotExist:
                        tilt_value[key] = None
                except:
                    tilt_value[key] = Annotation.objects.get(task=child_task, label=val[0]).text

    return tilt_value


def create_tilt(id):
    # get root task
    root = Task.objects.get(id=id)
    while root.parent is not None:
        root = root.parent

    # populate tilt dict according to tilt schema file
    tilt_dict = {}
    for entry in Config.SCHEMA_DICT.keys():
        tilt_value = iterate_through_hierarchy_level(root, [entry])
        tilt_dict[entry] = tilt_value

    # Create Meta Object
    meta_document_obj = MetaTask.objects.get(root_task=root)
    meta_entry = Meta.from_db_document(meta_document_obj)
    meta_entry.generate_hash_entry(tilt_dict)

    # update hash for modified
    meta_document_obj._hash = meta_entry._hash
    meta_document_obj.save()

    # put meta first
    meta_entry = list(meta_entry.to_tilt_dict_meta().items())
    meta_entry.extend(tilt_dict.items())
    tilt_dict = dict(meta_entry)

    return tilt_dict
