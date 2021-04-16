from typing import Dict, List
from config import Config
import json
from database.models import Task
from tilt_resources.tilt_schema import TiltSchema


class DescriptonFinder:

    tilt_dict = Config.TILT_DICT

    def __init__(self) -> None:
        with open(Config.DESC_PATH, "r") as json_file:
            self.tilt_descriptions = json.load(json_file)
        tilt_schema = TiltSchema.create_schema_with_desc()
        self.schema_to_tilt_mapping = {node.desc: node for node in tilt_schema.node_list if node.desc}

    def _get_path_node_names(self, label: str, task_parent: 'Task'):
        node = self.schema_to_tilt_mapping[label]
        label_chain = [path_node.name for path_node in node.path if path_node.name != '']
        return label_chain

    def _find_description_by_label_chain(self, label_chain: List[str],
                                         tilt_dict: Dict[str, str] = None) -> str:

        # TODO: here write the conditions for navigation through the description json
        if label_chain != [] and tilt_dict:
            label = label_chain.pop(0)
            tilt_entry = self._get_entry_from_tilt_dict(label, tilt_dict)
            description = self._find_description_by_label_chain(label_chain, tilt_entry)
        else:
            description = tilt_dict["description"]

        return description

    def find_descriptions(self, task: 'Task') -> Dict[str, str]:
        label_descriptions = {}
        for label in task.labels:
            label_chain = self._get_path_node_names(label, task.parent)
            label_descriptions[label] = self._find_description_by_label_chain(
                label_chain,
                tilt_dict=self.tilt_descriptions
                )
        return label_descriptions

    def _get_entry_from_tilt_dict(self, label: str, tilt_dict: dict) -> str:
        desc = tilt_dict.get(label)
        if not desc:
            if tilt_dict.get("additionalProperties"):
                desc = tilt_dict["properties"][label]
            if tilt_dict.get("additionalItems"):
                desc = tilt_dict["items"]["anyOf"][0]
                desc = self._get_entry_from_tilt_dict(label=label, tilt_dict=desc)
        return desc
