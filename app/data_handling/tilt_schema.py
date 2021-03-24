import json
import os
from typing import List
import torch
from dataclasses import dataclass

from config import Config


class TiltSchema:

    _default_json_path = os.path.join(Config.BASE_PATH, "tilt/schema.json")

    def __init__(self, json_tilt_dict: dict):
        self.node_list, edge_list = self._create_graph(json_tilt_dict=json_tilt_dict)
        self.edge_list = self._flatten_hierarchy(edge_list)
        self.adjacency_matrix = self._form_adjacency_matrix(self.edge_list)

    @classmethod
    def create_from_json(cls, json_path: str = None):
        if not json_path:
            json_path = cls._default_json_path

        with open(json_path, "r") as json_file:
            json_dict = json.load(json_file)
        return cls(json_tilt_dict=json_dict)

    def _create_graph(self, json_tilt_dict: dict, parent: 'TiltNode' = None) -> List['TiltNode']:
        node_list = []
        edge_list = []
        sub_node_list = []
        for key, dict_item in json_tilt_dict.items():
            if isinstance(dict_item, dict):
                sub_parent = self._find_parent(dict_item)
                sub_nodes, sub_edges = self._create_graph(dict_item, sub_parent)
                sub_node_list.extend(sub_nodes)
                node_list.append(sub_parent)
                edge_list.append(sub_edges)

            if isinstance(dict_item, str) and key not in ["desc", "key"]:
                tilt_node = TiltNode(name=dict_item, value=None, parent=None)
                node_list.append(tilt_node)

        if parent:
            for tilt_node in node_list:
                if isinstance(tilt_node, TiltNode):
                    tilt_node.set_parent(parent)
                    edge = Edge(origin=parent.node_id,
                                target=tilt_node.node_id)
                    edge_list.append(edge)
        if sub_node_list != []:
            node_list.extend(sub_node_list)
        return node_list, edge_list

    @staticmethod
    def _find_parent(json_tilt_dict: dict, value: str = None) -> 'TiltNode':
        desc = json_tilt_dict.get("desc", None)
        node = TiltNode(name=desc, value=value, parent=None)
        return node

    def _flatten_hierarchy(self, nested_list: List) -> List:
        pass

    def _form_adjacency_matrix(self, edges_list: List) -> torch.Tensor:
        pass


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


@dataclass
class Edge:
    origin: int
    target: int
    hierarchy: int = None


if __name__ == "__main__":
    tilt_schema = TiltSchema.create_from_json()
    node = TiltNode()
    node2 = TiltNode()
    node3 = TiltNode()
    print(node.node_id)
    print(node2.node_id)
    print(node.node_id)
    print(node3.node_id)
