from typing import Dict, List, Tuple
import uuid

from database.models import Task, Annotation
from config import Config
from utils.label import Label


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
        schema_level = self._retrieve_schema_level(self.task.hierarchy)
        for annotation in annotations:
            for schema_key, schema_value in schema_level.items():
                schema_value = schema_value[0] if isinstance(schema_value, list) else schema_value
                if isinstance(schema_value, dict) and self._subtasks_needed(schema_value, annotation):
                    labels, desc_keys, id_annotation = self._process_dict_entry(schema_value)
                    new_task_hierarchy = self.task.hierarchy + [schema_key]

                    text = annotation.text if len(annotation.text) <= 20 else annotation.text[:20] + '...'
                    name = annotation.label + ' (' + text + ')' + ' - ' + self.task.name
                    new_task = Task(name=name, labels=labels,
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
                    if id_annotation:
                        self._create_id_annotation(new_task)

    def _process_dict_entry(self, dict_entry: Dict) -> Tuple[List, List]:
        labels = []
        desc_keys = []
        id_annotation = False
        for dict_key, dict_value in dict_entry.items():
            if dict_key.startswith("_"):
                if dict_key == "_id":
                    id_annotation = True
                continue
            if dict_key.startswith("~"):
                continue
            label = self._create_label(dict_value).to_dict()
            labels.append(label)
            desc_keys.append(dict_key)

        return labels, desc_keys, id_annotation

    # TODO: give IDs, but tag annotations that should not be shown in frontend

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

    def _create_label(self, dict_value):
        if isinstance(dict_value, str):
            return Label(dict_value, multiple=False)
        try:
            dict_value = dict_value[0]
            multiple = True
        except KeyError:
            multiple = False
        return Label(name=dict_value["_desc"], multiple=multiple)

    def _create_id_annotation(self, task):
        annotation = Annotation(task=task,
                                label="_id",
                                text=str(uuid.uuid4()),
                                start=0,
                                end=0)
        annotation.save()
