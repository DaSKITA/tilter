from mongoengine import DoesNotExist
from typing import Union, Tuple
from database.models import Annotation


class AnnotationHandler:

    def __init__(self) -> None:
        self.all_current_annotations = []
        self.new_annotations = []

    def get_annotation(self, task=None, text=None, start=None, end=None, label=None) -> Union[Annotation, None]:
        try:
            annotation = Annotation.objects.get(task=task, text=text, start=start, end=end, label=label)
        except DoesNotExist:
            print(Warning(f"Annotation {label} does not exist!"))
            annotation = None
        return annotation

    def create_and_save_annotation(self, task=None, text=None, start=None, end=None, label=None,
                                   return_annotation=False) -> Tuple[bool, Union[Annotation, None]]:
        annotation = self.get_annotation(task=task, text=text, start=start, end=end, label=label)
        if not annotation:
            annotation = Annotation(task=task, text=text, start=start, end=end, label=label)
            annotation.save()
            created = True
        else:
            print(f"Annotation {annotation.label} already exists!")
            created = False
        return created, annotation if return_annotation else None

    def delete(self, annotation=None):
        if annotation:
            annotation.delete()
            print(f"Deleted Annotation with Label: {annotation.label}")

    def filter_new_annotations(self, annotation_list):
        for annotation_arguments in annotation_list:
            created, annotation = self.create_and_save_annotation(**annotation_arguments,
                                                                  return_annotation=True)
            if created:
                self.new_annotations.append(annotation)
            self.all_current_annotations.append(annotation)
        return self.new_annotations, self.all_current_annotations

    def synch_task_annotations(self, task, current_annotation_list):
        for anno in Annotation.objects(task=task):
            if anno.id not in current_annotation_list:
                self.delete(anno)
