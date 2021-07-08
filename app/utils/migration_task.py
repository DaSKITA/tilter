from abc import ABC, abstractmethod
from mongoengine.errors import DoesNotExist
from database.models import Task, Annotation, LinkedAnnotation
from typing import List, Dict
from config import Config
from mongoengine import connect
from tqdm import tqdm
from tilt_resources.annotation_handler import AnnotationHandler


class MigrationTask(ABC):
    connect(**Config.MONGODB_SETTINGS)

    @abstractmethod
    def run_migration():
        pass


class HtmlTaskTag(MigrationTask):

    @staticmethod
    def run_migration():
        for task in tqdm(Task.objects):
            task.update(html=False)


class SubtaskAnnotation(MigrationTask):

    @staticmethod
    def get_tied_annotation_values(
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
        parent_annotation = None
        child_annotation = None
        schema_key = hierachy_list.pop(0)
        if isinstance(tilt_schema[schema_key], list):
            for idx, _ in enumerate(tilt_schema[schema_key]):
                if hierachy_list == []:
                    parent_annotation, child_annotation = SubtaskAnnotation._identify_parent_child_annotation_pair(
                        tilt_schema[schema_key][idx], annotation)
                else:
                    parent_annotation, child_annotation = SubtaskAnnotation.get_tied_annotation_values(
                        hierachy_list=hierachy_list,
                        tilt_schema=tilt_schema[schema_key][idx],
                        annotation=annotation)
        else:
            if hierachy_list == []:
                parent_annotation, child_annotation = SubtaskAnnotation._identify_parent_child_annotation_pair(
                        tilt_schema[schema_key], annotation)
            else:
                parent_annotation, child_annotation = SubtaskAnnotation.get_tied_annotation_values(
                    hierachy_list=hierachy_list,
                    tilt_schema=tilt_schema[schema_key],
                    annotation=annotation
                )
        return parent_annotation, child_annotation

    @staticmethod
    def _identify_parent_child_annotation_pair(tilt_schema, annotation):
        subtask_dict = SubtaskAnnotation._get_subtask_dict(annotation, tilt_schema)
        child_key = [schema_idx for schema_idx, schema_value in tilt_schema.items()
                     if annotation.label == schema_value]
        parent_annotation = None
        child_annotation = None
        try:
            child_key = child_key[0]
        except IndexError:
            pass

        if child_key == tilt_schema["_key"]:
            parent_annotation = SubtaskAnnotation._determine_parent_annotation(tilt_schema, annotation)
        elif isinstance(subtask_dict, dict):
            child_annotation = SubtaskAnnotation._determine_child_annotation(annotation, subtask_dict)
        return parent_annotation, child_annotation

    @staticmethod
    def _determine_child_annotation(annotation, subtask_dict):
        annotation_task = annotation.task
        subtask_annot_key = subtask_dict["_key"]
        subtask_label = subtask_dict[subtask_annot_key]
        child_tasks = Task.objects(parent=annotation_task)
        for child_task in child_tasks:
            try:
                child_task_annotation = Annotation.objects.get(
                    task=child_task, label=subtask_label, text=annotation.text)
                break
            except DoesNotExist:
                child_task_annotation = None
        return child_task_annotation

    @staticmethod
    def _determine_parent_annotation(tilt_schema, annotation):
        parent_task = annotation.task.parent
        parent_label = tilt_schema["_desc"]
        try:
            parent_annotation = Annotation.objects.get(task=parent_task, label=parent_label, text=annotation.text,
                                                       start=annotation.start, end=annotation.end)
        except DoesNotExist:
            parent_annotation = None
        return parent_annotation

    @staticmethod
    def run_migration():
        tilt_schema = Config.SCHEMA_DICT
        for annotation in tqdm(Annotation.objects):
            annotation_task = annotation.task
            annotation_hierarchy = list(annotation_task.hierarchy)
            if annotation_hierarchy != []:
                parent_annotation, child_annotation = SubtaskAnnotation.get_tied_annotation_values(
                    annotation=annotation, hierachy_list=annotation_hierarchy, tilt_schema=tilt_schema)
            else:
                parent_annotation, child_annotation = SubtaskAnnotation.define_root_annotation_ties(
                    annotation, tilt_schema)
            print(f"Updating Annotation: {annotation.label}")
            annotation.update(parent_annotation=parent_annotation)
            annotation.update(child_annotation=child_annotation)

    @staticmethod
    def define_root_annotation_ties(annotation, tilt_schema):
        subtask_dict = SubtaskAnnotation._get_subtask_dict(annotation, tilt_schema)
        parent_annotation = None
        child_annotation = SubtaskAnnotation._determine_child_annotation(annotation, subtask_dict)
        return parent_annotation, child_annotation

    @staticmethod
    def _get_subtask_dict(annotation, tilt_schema):
        annotation_task = annotation.task
        task_labels = annotation_task.labels

        for label in task_labels:
            if label["name"] == annotation.label:
                annotation_key = label["tilt_key"]
                break
            else:
                annotation_task = None
        subtask_dict = tilt_schema[annotation_key]
        if isinstance(subtask_dict, list):
            return subtask_dict[0]
        else:
            return subtask_dict


class DeleteUnboundObj:

    @staticmethod
    def run_migration():
        annotation_handler = AnnotationHandler()
        for annotation in Annotation.objects:
            try:
                parent_chain = []
                annotation_task = annotation.task
                parent_chain = DeleteUnboundObj.get_task_chain(annotation_task, parent_chain)
            except DoesNotExist:
                annotation.delete()
                [annotation_handler._delete_task_objects(task) for task in parent_chain]
                [task.delete() for task in parent_chain]
                print("Delete all tasks and annotations with unclear paths")

    @staticmethod
    def get_task_chain(annotation_task, task_list):
        task_list = task_list + [annotation_task]
        if annotation_task.parent:
            task_list = DeleteUnboundObj.get_task_chain(annotation_task.parent, task_list)
        return task_list

    @staticmethod
    def delete_task_elements(task):
        task_annotations = Annotation.objects(task=task)
        linked_task_annotations = LinkedAnnotation.objects(task=task)
        [task_annotation.delete() for task_annotation in task_annotations]
        [task_annotation.delete() for task_annotation in linked_task_annotations]
