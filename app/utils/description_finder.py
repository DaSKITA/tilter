from typing import Dict, List
from config import Config
import json
from database.models import Task
from utils.label import Label


class DescriptonFinder:

    def __init__(self) -> None:

        """
        Finds all necessary descriptions for a provided task.
        Task items store a "desc_keys" attribute which refers to the desciption keys in 'tilt_desctitions'.
        """
        with open(Config.DESC_PATH, "r") as json_file:
            self.tilt_descriptions = json.load(json_file)

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
            label = label_chain.pop(0)
            tilt_entry = self._get_entry_from_tilt_desc_dict(label, tilt_dict)
            if type(tilt_entry) != str:
                description = self._find_description_by_label_chain(label_chain, tilt_entry)
            else:
                return tilt_entry
        else:
            description = tilt_dict["description"]
        return description

    def find_descriptions(self, task: 'Task') -> Dict[str, str]:
        """
        Finds all descriptions for a provided task and returns these descriptions in a dictionary.
        Key = Label_name
        Value = Description

        Args:
            task (Task): [description]

        Returns:
            Dict[str, str]: [description]
        """
        label_descriptions = {}
        for idx, desc_label in enumerate(task.desc_keys):
            label_chain = task.hierarchy + [desc_label]
            label_descriptions[Label(**task.labels[idx]).name] = self._find_description_by_label_chain(
                label_chain,
                tilt_dict=self.tilt_descriptions
                )
        return label_descriptions

    def _get_entry_from_tilt_desc_dict(self, label: str, tilt_dict: dict) -> str:
        """
        Retrieves entries form the Tilt_Description Dictionary. The dictionary stores properties in
        subdictionaries under 'properties'. Entries that are part of Tilt List entries are stored in a list
        under 'item' -> 'anyOf'. The retrieved list stores a dictionary which follows above mentioned pattern
        for 'properties'. Description of items can be found under "description" if the provided label has
        an entry in the dictionary.

        Args:
            label (str): [description]
            tilt_dict (dict): [description]

        Returns:
            str: [description]
        """
        desc = tilt_dict.get(label)
        if not desc:
            if tilt_dict.get("additionalProperties"):
                desc = tilt_dict["properties"][label]
            if tilt_dict.get("additionalItems"):
                desc = tilt_dict["items"]["anyOf"][0]
                desc = self._get_entry_from_tilt_desc_dict(label=label, tilt_dict=desc)
        return desc
