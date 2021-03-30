from typing import List, Dict

from database.models import Annotation
from tilt_resources.tilt_schema import TiltSchema


class TiltCreator:

    def __init__(self) -> None:
        """
        Creates a TiltDocument from annotations.
        This class uses the TiltSchema to write annotations into a reasonable representation.
        The schema is transformed to a dictionary - this dictionary can be seen as a tilt document.
        """
        self.tilt_schema = TiltSchema.create_schema_with_desc()

    def create_tilt_document(self, annotation_list: List['Annotation']) -> Dict[str, object]:
        """
        Iterates through all relevant annotations and uses these annotations to create a tilt document.
        The tilt document is a dictionary.

        Args:
            annotation_list (List[): [description]

        Returns:
            Dict[str, object]: [description]
        """
        tilt_obj_dict = {}
        for annotation in annotation_list:
            self._create_tilt_class_from_annot(annotation)
        tilt_obj_dict = self.tilt_schema.to_dict()
        return tilt_obj_dict

    def _create_tilt_class_from_annot(self, annotation: str) -> Dict[str, object]:
        """
        Matches the annotation label with the description of a single node. If both are identical,
        the annotation.text will be given to the node.value. The node.desc is the description of a tiltnode,
        which is exposed to the frontend user.

        Args:
            annotation (str): [description]

        Returns:
            Dict[str, object]: [description]
        """
        [node.set_value(annotation.text)
         for node in self.tilt_schema.node_list if node.desc == annotation.label]
