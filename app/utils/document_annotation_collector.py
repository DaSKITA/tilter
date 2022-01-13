from database.models import Task, Annotation
from mongoengine import DoesNotExist


class DocumentAnnotationCollector:

    def __init__(self) -> None:
        """
        This classs creates a list of annotations for given documents. It is used to create training data out
        of all documents or a supplied document.
        """
        pass

    def create_annotation_dict(self, root_task=None) -> dict:
        task_list = self.create_task_list(root_task)
        annotation_list = self.get_annotation_list(task_list)
        document_information = dict(document_name=root_task.name, text=root_task.text)
        annotation_dict = [self.get_annotation_information(annotation) for annotation in annotation_list]
        return dict(document=document_information, annotations=annotation_dict)

    def create_task_list(self, root_task):
        tasks = []
        if root_task:
            try:
                tasks += Task.objects(parent=root_task)
                for task in tasks:
                    tasks += self.create_task_list(task)
            except DoesNotExist:
                return tasks
        return tasks

    def get_annotation_list(self, task_list):
        """This function searches for annotations in a given task list. This currently does not include
        HiddenAnnotations and LinkedAnnotations.

        Args:
            task_list ([type]): [description]

        Returns:
            [type]: [description]
        """
        annotations_list = []
        for task in task_list:
            annotations = Annotation.objects(task=task)
            annotations = self.fix_annotation_labels(annotations, task)
            annotations_list += annotations
        return annotations_list

    def get_annotation_information(self, annotation):
        return dict(
            annotation_label=annotation.label,
            annotation_text=annotation.text,
            annotation_start=annotation.start,
            annotation_end=annotation.end
        )

    def fix_annotation_labels(self, annotations, task):
        """
        As annotations in their base form do not have a hierarchy indication in their label name, they need to
        be added herein. The recommended practice would be to incorpoerate a proper name during the task
        creation.

        Args:
            annotations ([type]): [description]
            task ([type]): [description]

        Returns:
            [type]: [description]
        """
        for annotation in annotations:
            annotation.label = "--".join(task.hierarchy) + "--" + f"{annotation.label}"
        return annotations
