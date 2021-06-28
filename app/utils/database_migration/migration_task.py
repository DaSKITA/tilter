from abc import ABC, abstractmethod
from database.models import Task, Annotation
from typing import List, Dict
from config import Config


class MigrationTask(ABC):

    @abstractmethod
    def run_migration():
        pass


class HtmlTaskTag(MigrationTask):

    def run_migration():
        for task in Task.objects:
            task.update(html=True)


class SubtaskAnnotation(MigrationTask):

    def get_tied_annotation_values(self,
                                   hierachy_list: List,
                                   tilt_schema: Dict = None, annotation: Annotation = None):
        """
        Iterates through the tilt schema and applies a supplied function.

        Args:
            hierachy_list (List): [description]
            tilt_schema (Dict, optional): [description]. Defaults to None.
            supplied_callable (Callable, optional): [description]. Defaults to None.

        Raises:
            AttributeError: [description]

        Returns:
            [type]: [description]
        """
        schema_key = hierachy_list.pop(0)
        if isinstance(tilt_schema, list):
            for idx, _ in enumerate(tilt_schema):
                if hierachy_list == []:
                    if not tilt_schema[idx].get(schema_key):
                        iteration_return_value = self._identify_parent_child_annotation_pair(
                            schema_key, tilt_schema, annotation)
                else:
                    iteration_return_value = self.iterate_through_tilt_schema(
                        hierachy_list=hierachy_list,
                        tilt_schema=tilt_schema[schema_key])
        else:
            if hierachy_list == []:
                if not tilt_schema.get(schema_key):
                    iteration_return_value = self._identify_parent_child_annotation_pair(
                            schema_key, tilt_schema, annotation)
            else:
                iteration_return_value = self.iterate_through_tilt_schema(
                    hierachy_list=hierachy_list,
                    tilt_schema=tilt_schema[schema_key]
                )
        return iteration_return_value

    def _identify_parent_child_annotation_pair(self, schema_key, tilt_schema, annotation):
        subtask_dict = tilt_schema[schema_key][annotation.label]
        child_key = [schema_idx for schema_idx, schema_value in tilt_schema[schema_key]
                     if annotation.label == schema_value]
        try:
            subtask_dict = subtask_dict[0]
        except KeyError:
            pass
        parent_annotation = None
        child_annotation = None
        try:
            child_key = child_key[0]
        except IndexError:
            return "No key found for annotation label."
        if child_key == tilt_schema[schema_key]["_key"]:
            child_annotation = annotation
            parent_annotation = self._determine_parent_annotation(child_key, tilt_schema[schema_key],
                                                                  annotation)
        elif isinstance(subtask_dict, dict):
            parent_annotation = annotation
            child_annotation = self._determine_child_annotation(annotation, subtask_dict)
        return parent_annotation, child_annotation

    def _determine_child_annotation(self, annotation, subtask_dict):
        annotation_task = annotation.task
        subtask_label = subtask_dict["_desc"]
        child_tasks = Task.objects.get(parent=annotation_task)
        for child_task in child_tasks:
            child_task_annotation = Annotation.objects.get(task=child_task, label=subtask_label,
                                                           text=annotation.text)
            if child_task_annotation:
                return child_task_annotation
        return None

    def _determine_parent_annotation(self, schema_key, tilt_schema, annotation):
        parent_task = annotation.task.parent
        parent_label = tilt_schema[schema_key]["_desc"]
        parent_annotation = Annotation.objects.get(task=parent_task, label=parent_label)
        return parent_annotation

    def run_migration(self):
        tilt_schema = Config.SCHEMA_DICT
        for annotation in Annotation.objects:
            print(f"Updating Annotation: {annotation.label}")
            annotation_task = annotation.task
            annotation_hierarchy = annotation_task.hierarchy
            parent_annotation, child_annotation = self.get_tied_annotation_values(
                annotation=annotation, hierachy_list=annotation_hierarchy, tilt_schema=tilt_schema)
            annotation.update(parent_annotation=parent_annotation)
            annotation.update(child_annotation=child_annotation)
