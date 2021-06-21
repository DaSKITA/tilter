from dataclasses import asdict, dataclass
from typing import Dict, List
from config import Config
import json
from utils.label import LabelFactory


class DescriptonFinder:

    def __init__(self) -> None:

        """
        Finds all necessary descriptions for a provided task.
        Task items store a "desc_keys" attribute which refers to the desciption keys in 'tilt_desctitions'.
        """
        with open(Config.DESC_PATH, "r") as json_file:
            self.tilt_descriptions = json.load(json_file)
        self.exception_list = {
            "recipientsOnlyCategory": "category"
        }

    def _find_description_by_label_chain(self, label_chain: List[str],
                                         tilt_dict: Dict[str, str] = None) -> str:
        """
        Recursively iterate through the tilt_descriptions dict with the label chain,
        to get a label description. Before the function is called recursively the respective dict entry from
        the label is retrieved. The retrieval requires some conditions.

        Args:
            label_chain (List[str]): [description]
            tilt_dict (Dict[str, str], optional): [description]. Defaults to None.

        Returns:
            str: [description]
        """
        if label_chain != [] and tilt_dict:
            label_name = label_chain.pop(0)
            tilt_entry = self._get_entry_from_tilt_desc_dict(label_name, tilt_dict)
            if type(tilt_entry) != str:
                description = self._find_description_by_label_chain(label_chain, tilt_entry)
            else:
                return tilt_entry
        else:
            try:
                description = tilt_dict["description"]
            except KeyError:
                print(Warning(f"Could not find description key in {tilt_dict}"))
                description = "No description found!"
        return description

    def find_descriptions(self, task_labels, task_hierarchy) -> Dict[str, str]:
        """
        Finds all descriptions for a provided task and returns these descriptions in a dictionary.
        Key = Label_name
        Value = Description

        Args:
            task (Task): [description]

        Returns:
            Dict[str, str]: [description]
        """
        descriptions_collection = DescriptionCollection()
        label_factory = LabelFactory()
        for idx, label in enumerate(task_labels):
            label = label_factory.create_label(task_labels[idx])
            label_chain = task_hierarchy + [label.tilt_key]
            description_text = self._find_description_by_label_chain(
                label_chain,
                tilt_dict=self.tilt_descriptions
                )
            description = TiltElementDescription(name=label.name, description=description_text)
            descriptions_collection.append_description(description)
        return descriptions_collection

    def _get_entry_from_tilt_desc_dict(self, label_name: str, tilt_dict: dict) -> str:
        """
        Retrieves entries form the Tilt_Description Dictionary. The dictionary stores properties in
        subdictionaries under 'properties'. Entries that are part of Tilt List entries are stored in a list
        under 'item' -> 'anyOf'. The retrieved list stores a dictionary which follows above mentioned pattern
        for 'properties'. Description of items can be found under "description" if the provided label_name has
        an entry in the dictionary.

        Args:
            label_name (str): [description]
            tilt_dict (dict): [description]

        Returns:
            str: [description]
        """
        desc = tilt_dict.get(label_name)
        if not desc:
            if tilt_dict.get("additionalProperties"):
                try:
                    desc = tilt_dict["properties"][label_name]
                except KeyError:
                    label_name = self.exception_list[label_name]
                    desc = tilt_dict["properties"][label_name]
            if tilt_dict.get("additionalItems"):
                desc = tilt_dict["items"]["anyOf"][0]
                desc = self._get_entry_from_tilt_desc_dict(label_name=label_name, tilt_dict=desc)
        return desc


class DescriptionCollection:

    def __init__(self) -> None:
        self.descriptions: List[TiltElementDescription] = []

    def append_description(self, annotation_desc):
        self.descriptions.append(annotation_desc)

    def get_descriptions(self):
        return self._get_dict_list(self.descriptions)

    def _get_dict_list(self, description_storage):
        return [description.to_dict() for description in description_storage]


@dataclass
class TiltElementDescription:
    name: str = None
    description: str = None

    def to_dict(self):
        return asdict(self)
