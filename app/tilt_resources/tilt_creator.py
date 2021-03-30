from typing import List, Dict

from database.models import Annotation
from tilt_resources.tilt_schema import TiltSchema


class TiltCreator:

    def __init__(self) -> None:
        self.tilt_schema = TiltSchema.create_schema_with_desc()

    def create_tilt_document(self, annotation_list: List['Annotation']) -> Dict[str, object]:
        tilt_obj_dict = {}
        for annotation in annotation_list:
            _ = self._create_tilt_class_from_annot(annotation)
        tilt_obj_dict = self.tilt_schema.to_dict()
        return tilt_obj_dict

    def _create_tilt_class_from_annot(self, annotation: str) -> Dict[str, object]:
        [node.set_value(annotation.text)
         for node in self.tilt_schema.node_list if node.desc == annotation.label]
