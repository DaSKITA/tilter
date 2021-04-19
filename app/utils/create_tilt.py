from database.models import Task, Annotation
from mongoengine import DoesNotExist
import os
import json

# open tilt schema file
cur_path = os.path.dirname(__file__)
new_path = os.path.join(cur_path, '..', 'tilt_resources', 'schema.json')
with open(new_path, 'r') as f:
    schema = json.load(f)

def iterate_through_hierarchy_level(parent_task, hierarchy):
    local_schema = schema.copy()
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
        else:
            # iterate through current schema hierarchy
            if type(local_schema) is dict:
                tilt_value_part = {}
                for key, val in local_schema.items():
                    annotations = Annotation.objects(task=parent_task, label=local_schema["desc"])
                    if key in ['desc', 'key']:
                        continue
                    annotations_list = [anno.text for anno in annotations]
                    tilt_value_part[key] = annotations_list
                tilt_value.append(tilt_value_part)
            else:
                if local_schema == "dict":
                    raise DoesNotExist
                annotations = Annotation.objects(task=parent_task, label=local_schema)
                tilt_value = [anno.text for anno in annotations]

    # if not label_limited:
    #     tilt_value = []
    #     for task in tasks:
    #         tilt_value_part = {}
    #         # iterate through current schema hierarchy
    #         for key, val in local_schema.items():
    #             if type(val) in [dict, list]:
    #                 new_hierarchy = hierarchy.copy()
    #                 new_hierarchy.append(key)
    #                 tilt_value_part[key] = iterate_through_hierarchy_level(task, new_hierarchy)
    #             elif key in ['desc', 'key']:
    #                 continue
    #             else:
    #                 try:
    #                     tilt_value_part[key] = Annotation.objects.get(task=task, label=val).text
    #                 except DoesNotExist:
    #                     tilt_value_part[key] = None
    #                 except:
    #                     tilt_value_part[key] = Annotation.objects.get(task=task, label=val[0]).text
    #         tilt_value.append(tilt_value_part)

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
    for entry in schema.keys():
        tilt_value = iterate_through_hierarchy_level(root, [entry])
        tilt_dict[entry] = tilt_value

    return tilt_dict