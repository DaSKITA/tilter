from mongoengine import DoesNotExist
from typing import Union, Tuple, List
from database.models import Annotation, LinkedAnnotation, Task


class AnnotationHandler:

    def __init__(self) -> None:
        self.all_current_annotations = []
        self.new_annotations = []

    def get_annotation(self, task=None, text=None, start=None, end=None, label=None, annotation_class=None) -> Union[Annotation, None]:
        """Retrieves an Annotation by values. If the Annotation does not exist an error is thrown.

        Args:
            task ([type], optional): [description]. Defaults to None.
            text ([type], optional): [description]. Defaults to None.
            start ([type], optional): [description]. Defaults to None.
            end ([type], optional): [description]. Defaults to None.
            label ([type], optional): [description]. Defaults to None.

        Returns:
            Union[Annotation, None]: [description]
        """
        try:
            annotation = Annotation.objects.get(task=task, text=text, start=start, end=end, label=label)
        except DoesNotExist:
            print(Warning(f"Annotation {label} does not exist!"))
            annotation = None
        return annotation

    def create_and_save_annotation(self, task: Task = None, text: str = None, start: float = None,
                                   end: float = None, label: str = None,
                                   return_annotation=False) -> Tuple[bool, Union[Annotation, None]]:
        """Creates an nnotation. Before the annotation is created it is checked, whether it already exists in
        the database. If it existed already the boolean value in the returned tuple will be set to false.

        Args:
            task ([type], optional): [description]. Defaults to None.
            text ([type], optional): [description]. Defaults to None.
            start ([type], optional): [description]. Defaults to None.
            end ([type], optional): [description]. Defaults to None.
            label ([type], optional): [description]. Defaults to None.
            return_annotation (bool, optional): [description]. Defaults to False.

        Returns:
            Tuple[bool, Union[Annotation, None]]: [description]
        """
        annotation = self.get_annotation(task=task, text=text, start=start, end=end, label=label)
        if not annotation:
            annotation = Annotation(task=task, text=text, start=start, end=end, label=label)
            annotation.save()
            created = True
        else:
            print(f"Annotation {annotation.label} already exists!")
            created = False
        return created, annotation if return_annotation else None

    def delete(self, annotation: Annotation = None):
        if annotation:
            annotation.delete()
            print(f"Deleted Annotation with Label: {annotation.label}")

    def filter_new_annotations(self, annotation_list: List[Annotation]):
        """
        Filters our new annotations from a list of given annotation values. Every new annotation will be
        created. A list of newly created annotations, and all annotations generated from the provided list
        will be created.

        Args:
            annotation_list ([type]): [description]

        Returns:
            [type]: [description]
        """
        for annotation_arguments in annotation_list:
            created, annotation = self.create_and_save_annotation(**annotation_arguments,
                                                                  return_annotation=True)
            if created:
                self.new_annotations.append(annotation)
            self.all_current_annotations.append(annotation.id)
        return self.new_annotations, self.all_current_annotations

    def synch_task_annotations(self, task: Task, current_annotation_list: List[Annotation]):
        """
        Deletes annotations in the list from the database that are not part of the provided task.

        Args:
            task ([type]): [description]
            current_annotation_list ([type]): [description]
        """
        for anno in Annotation.objects(task=task):
            if anno.id not in current_annotation_list:
                self.delete(anno)
            else:
                self.synch_linked_annotations(related_annotation=anno, task=task)

    def synch_linked_annotations(self, task, related_annotation: None):
        try:
            linked_annotations = LinkedAnnotation.objects(related_to=related_annotation, task=task)
            for linked_annotation in linked_annotations:
                linked_annotation.value = True
                linked_annotation.save()
        except DoesNotExist:
            print("No linked Annotations found.")

    def create_manual_annotations(self, manual_bools_dict, task):
        for manual_bool_label, manual_bool_value in manual_bools_dict.items():
            try:
                manual_bool_annotation = LinkedAnnotation.objects.get(task=task,
                                                                     manual=True,
                                                                     value=manual_bool_value,
                                                                     label=manual_bool_label)
                print("Manual Annotation already exists. Overwriting...")
                manual_bool_annotation.value = manual_bool_value
            except DoesNotExist:
                manual_bool_annotation = LinkedAnnotation(task=task, manual=True,
                                                          value=manual_bool_value,
                                                          label=manual_bool_label)
            manual_bool_annotation.save()
