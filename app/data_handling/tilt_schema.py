import json
import os
from typing import List

from config import Config


class TiltSchema:

    _default_json_path = os.path.join(Config.BASE_PATH, "tilt/schema.json")

    def __init__(self, json_tilt_dict: dict):
        self.node_list = self._create_nodes(json_tilt_dict=json_tilt_dict)

    @classmethod
    def create_from_json(cls, json_path: str = None):
        if not json_path:
            json_path = cls._default_json_path

        with open(json_path, "r") as json_file:
            json_dict = json.load(json_file)
        return cls(json_tilt_dict=json_dict)

    def _create_nodes(self, json_tilt_dict: dict, parent: 'TiltNode' = None) -> List['TiltNode']:
        node_list = []
        for key, dict_item in json_tilt_dict.items():
            if isinstance(dict_item, dict):
                parent = self._find_parent(dict_item)
                subnodes = self._create_nodes(dict_item, parent)
                node_list.append(subnodes)

            if isinstance(dict_item, str) and key not in ["desc", "key"]:
                node_list.append(TiltNode(name=dict_item, value=None, parent=None))

        if parent:
            node_list = [tilt_node.set_parent(parent) for tilt_node in node_list
                         if isinstance(TiltNode, TiltNode)]

        return node_list

    def _get_dict_names(self, dict_obj: dict) -> List[str]:
        return list(dict.values())

    def _find_parent(self, json_tilt_dict: dict) -> 'TiltNode':
        desc = json_tilt_dict.get("desc", None)
        node = TiltNode(name=desc, value=None, parent=None)
        return node


class TiltNode:
    node_id = 0

    def __init__(self, name: str = None,
                 value: str = None,
                 parent: 'TiltNode' = None):
        TiltNode.node_id += 1
        self.node_id = TiltNode.node_id
        self.name = name
        self.value = value
        self.parent = parent

    def set_parent(self, parent):
        self.parent = parent


if __name__ == "__main__":
    tilt_schema = TiltSchema.create_from_json()
    node = TiltNode()
    node2 = TiltNode()
    node3 = TiltNode()
    print(node.node_id)
    print(node2.node_id)
    print(node.node_id)
    print(node3.node_id)
