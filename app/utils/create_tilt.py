from config import Config
from database.models import Task, Annotation, HiddenAnnotation, MetaTask, LinkedAnnotation
from mongoengine import DoesNotExist
from tilt_resources.meta import Meta
from tilt_resources.tilt_creator import TiltCreator


def get_recipients_from_category_only(annotations):
    recipients = []
    for annotation in annotations:
        recipient_from_annotation = {
            "name": None,
            "country": None,
            "division": None,
            "address": None,
            "representative": {
                "name": None,
                "email": None,
                "phone": None
            },
            "category": annotation.text
        }
        recipients.append(recipient_from_annotation)
    return recipients


def iterate_through_hierarchy_level(parent_task, hierarchy):
    local_schema = Config.SCHEMA_DICT.copy()
    label_limited = True

    # walk through schema using hierarchy
    for i in hierarchy:
        try:
            local_schema = local_schema[i]
        except:
            local_schema = local_schema[0][i]

    # if schema is of type list change cardinality and take note of limitation
    if type(local_schema) is list:
        local_schema = local_schema[0]
        label_limited = False

    # get all tasks that are associated as children of parent_task and are at the according hierarchy level
    tasks = Task.objects(parent=parent_task, hierarchy=hierarchy)

    if not label_limited:
        # there is no limitation regarding cardinality, so we expect a list of elements
        tilt_value = []
        if tasks:
            # there are subtasks of parent_task at the expected hierarchy level
            for task in tasks:
                tilt_value_part = {}
                # iterate through current schema hierarchy
                for key, val in local_schema.items():
                    # TODO: incorporate linked annotations
                    if key in ['_desc', '_key', "recipientsOnlyCategory"]:
                        continue
                    elif type(val) in [dict, list]:
                        val = val[0] if isinstance(val, list) else val
                        new_hierarchy = hierarchy.copy()
                        new_hierarchy.append(key)
                        tilt_value_part[key] = iterate_through_hierarchy_level(task, new_hierarchy)
                    elif key == "_id":
                        tilt_value_part[key] = HiddenAnnotation.objects.get(task=task, label=val).value
                    elif key.startswith("~"):
                        if val.startswith("#"):
                            tilt_value_part[key[1:]] = \
                                LinkedAnnotation.objects.get(task=task, label=key, manual=False).value
                        else:
                            try:
                                tilt_value_part[key[1:]] = \
                                    LinkedAnnotation.objects.get(task=task, label=key, manual=True).value
                            except DoesNotExist:
                                tilt_value_part[key[1:]] = "False"
                    elif key.startswith("_"):
                        try:
                            tilt_value_part[key] = Annotation.objects.get(task=task, label=val).text
                        except DoesNotExist:
                            tilt_value_part[key] = None
                    else:
                        try:
                            tilt_value_part[key] = Annotation.objects.get(task=task, label=val).text
                        except DoesNotExist:
                            tilt_value_part[key] = None
                tilt_value.append(tilt_value_part)

            # special case for recipientsOnlyCategory
            if hierarchy[-1] == "recipients":
                annotations = Annotation.objects(task=parent_task, label="Data Disclosed - Recipient Category Only")
                tilt_value += get_recipients_from_category_only(annotations)

        elif type(local_schema) is dict:
            # special case for recipientsOnlyCategory
            if hierarchy[-1] == "recipients":
                annotations = Annotation.objects(task=parent_task, label="Data Disclosed - Recipient Category Only")
                if annotations:
                    tilt_value += get_recipients_from_category_only(annotations)
                    return tilt_value
            # iterate through current schema hierarchy
            tilt_value_part = {}
            for key, val in local_schema.items():
                annotations = Annotation.objects(task=parent_task, label=local_schema["_desc"])
                if key in ['_desc', '_key']:
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
                val = val[0] if isinstance(val, list) else val
                new_hierarchy = hierarchy.copy()
                new_hierarchy.append(key)
                tilt_value[key] = iterate_through_hierarchy_level(child_task, new_hierarchy)
            elif key in ['_desc', '_key']:
                continue
            elif key.startswith("~"):
                if val.startswith("#"):
                    try:
                        tilt_value[key[1:]] = \
                            LinkedAnnotation.objects.get(task=child_task, label=key, manual=False).value
                    except DoesNotExist:
                        tilt_value[key[1:]] = None
                else:
                    try:
                        tilt_value[key[1:]] = \
                            LinkedAnnotation.objects.get(task=child_task, label=key, manual=True).value
                    except DoesNotExist:
                        tilt_value[key[1:]] = None
            else:
                try:
                    tilt_value[key] = Annotation.objects.get(task=child_task, label=val).text
                except DoesNotExist:
                    tilt_value[key] = None

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

    # TODO: this class needs to be extended
    tilt_creator = TiltCreator(tilt_dict)
    #tilt_creator.write_tilt_default_values()
    tilt_dict = tilt_creator.get_tilt_document()

    # Create Meta Object
    try:
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
    except DoesNotExist:
        print(Warning("MetaTask not present! Skipping Metaobject creation."))
    return tilt_dict
