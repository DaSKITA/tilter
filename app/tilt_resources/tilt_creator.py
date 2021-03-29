from typing import List, Dict
from tilt import tilt
from database.models import Annotation
from config import TiltMapping


class TiltCreator:

    def __init__(self) -> None:
        self.tilt_class_enum = TiltMapping

    def create_tilt_document(self, annotation_list: List['Annotation']) -> Dict[str, object]:
        tilt_obj_dict = {}
        for annotation in annotation_list:
            tilt_obj_dict = self._create_tilt_class_from_annot(annotation.label)
            tilt_doc_dict = tilt.Tilt(**tilt_obj_dict).to_dict()
        return tilt_doc_dict

    def _create_tilt_class_from_annot(self, annotation: str) -> Dict[str, object]:
        pass
