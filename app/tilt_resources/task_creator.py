from typing import Dict, List, Tuple
from collections import defaultdict

from database.models import Task, Annotation
from config import Config
from utils.label import AnnotationLabel, ManualBoolLabel, LinkedBoolLabel, IdLabel, Label, LabelEnum


class TaskCreator:

    def __init__(self, task: Task) -> None:
        self.schema = Config.SCHEMA_DICT
        self.task = task

    def _retrieve_schema_level(self, path_list: List[str]) -> Dict:
        hierarchy = self.schema
        for path_entry in path_list:
            try:
                hierarchy = hierarchy[path_entry]
            except TypeError:
                hierarchy = hierarchy[0][path_entry]
        if isinstance(hierarchy, list):
            hierarchy = hierarchy[0]
        return hierarchy

    def create_subtasks(self, annotations: List[Annotation]):
        """Basic Subtask Creation.
        Once an Annotation meets condition a new subtask with corresponding labels is created.
        Depending on the entries in the schema of the created task, the Labels vary in classes.
        Depending on the label class another routine is performed.

        Args:
            annotations (List[Annotation]): [description]
        """
        schema_level = self._retrieve_schema_level(self.task.hierarchy)
        for annotation in annotations:
            for schema_key, schema_value in schema_level.items():
                schema_value = schema_value[0] if isinstance(schema_value, list) else schema_value
                if isinstance(schema_value, dict) and self._subtasks_needed(schema_value, annotation):
                    labels, desc_keys = self._process_dict_entry(schema_value)
                    new_task_hierarchy = self.task.hierarchy + [schema_key]
                    label_dict = self._filter_labels(labels)

                    text = annotation.text if len(annotation.text) <= 20 else annotation.text[:20] + '...'
                    name = annotation.label + ' (' + text + ')' + ' - ' + self.task.name
                    new_task = Task(name=name, labels=label_dict[LabelEnum.ANNOTATION],
                                    hierarchy=new_task_hierarchy, parent=self.task,
                                    interfaces=[
                                        "panel",
                                        "update",
                                        "controls",
                                        "side-column",
                                        "predictions:menu"],
                                    html=self.task.html,
                                    text=self.task.text,
                                    desc_keys=desc_keys)
                    new_task.save()

                    new_task_anno_label = schema_value[schema_value['_key']] \
                        if type(schema_value[schema_value['_key']]) is not list \
                        else schema_value[schema_value['_key']][0]
                    # create annotation for new task
                    new_task_anno = Annotation(task=new_task, label=new_task_anno_label,
                                               text=annotation.text,
                                               start=annotation.start, end=annotation.end)
                    new_task_anno.save()
                    self._create_id_annotations(label_dict[LabelEnum.ID], new_task)

    def _process_dict_entry(self, dict_entry: Dict) -> Tuple[List, List]:
        """Performs different processing routines, depending on the dictionary key and dictionary value.
        Herein conditions for booleans and id fields are performed.

        Args:
            dict_entry (Dict): [description]

        Returns:
            Tuple[List, List]: [description]
        """
        labels = []
        desc_keys = []
        for dict_key, dict_value in dict_entry.items():
            label = None
            if dict_key.startswith("_"):
                if dict_key == "_id":
                    label = IdLabel(name="_id")
            elif dict_key.startswith("~"):
                if dict_value.startswith("#"):
                    label = LinkedBoolLabel(name=dict_key, linked_entry=dict_value.split("#")[1])
                else:
                    label = ManualBoolLabel(name=dict_key, manual_bool_entry=dict_value)
            else:
                label = self._create_annotation_label(dict_value)
            if label:
                labels.append(label)
                desc_keys.append(dict_key)
        return labels, desc_keys

    def _subtasks_needed(self, schema_value, annotation):
        """Evaluates necessary conditions for creating a subtask.

        Args:
            schema_value ([type]): [description]
            annotation ([type]): [description]

        Returns:
            [type]: [description]
        """
        annotation_equality = schema_value["_desc"] == annotation.label
        non_artificial = 1 < sum([not field.startswith("_") for field in schema_value.keys()])
        field_is_dict = any(isinstance(val, dict) for val in schema_value.values())
        return annotation_equality and (non_artificial or field_is_dict)

    def _create_annotation_label(self, dict_value):
        """Creates AnnotationLabel instances. These instances are pinned onto a task and provide
        basic annotation functionality in label studio.

        Args:
            dict_value ([type]): [description]

        Returns:
            [type]: [description]
        """
        if isinstance(dict_value, str):
            return AnnotationLabel(dict_value, multiple=False)
        try:
            dict_value = dict_value[0]
            multiple = True
        except KeyError:
            multiple = False
        return AnnotationLabel(name=dict_value["_desc"], multiple=multiple)

    def _create_id_annotations(self, id_labels, task):
        """Creates Annotations with IDs and saves them in the Database.

        Args:
            id_labels ([type]): [description]
            task ([type]): [description]
        """
        for id_label in id_labels:
            annotation = Annotation(task=task,
                                    label=id_label["name"],
                                    text=id_label["id_value"],
                                    start=0,
                                    end=0)
            annotation.save()

    def _filter_labels(self, label_list: List[Label]) -> Dict:
        """Filters Labels acording to their class and puts them into a dictionary.
        Each label type can be accessed directly via its class.

        Args:
            label_list (List[Label]): [description]

        Returns:
            Dict: [description]
        """
        label_dict = defaultdict(list)
        for label in label_list:
            label_dict[LabelEnum(label.__class__)].append(label.to_dict())
        return label_dict
