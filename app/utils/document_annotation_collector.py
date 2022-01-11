from database.models import Task, Annotation
from mongoengine import DoesNotExist


class DocumentAnnotationCollector:

    def __init__(self) -> None:
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
        annotations = []
        for task in task_list:
            annotations += Annotation.object(task=task).get()
            return annotations

    def get_annotation_information(self, annotation):
        return dict(
            annotation_label=annotation.label,
            annotation_text=annotation.text,
            annotation_start=annotation.start,
            annotation_end=annotation.end
        )
