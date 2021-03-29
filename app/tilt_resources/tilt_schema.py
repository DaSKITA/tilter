"This is just a first scetch, in case task creatinon should be changed"
import json
import os
from typing import List, Dict
from dataclasses import dataclass
import pandas as pd

from config import Config


class TiltSchema:

    _default_json_path = os.path.join(Config.BASE_PATH, "tilt_resources/tilt_schema.json")

    def __init__(self, json_tilt_dict: dict):
        self.node_list, self.edge_list = self._create_graph(json_tilt_dict=json_tilt_dict)
        self.adjacency_matrix = self._form_adjacency_matrix(self.edge_list)

    @classmethod
    def create_from_json(cls, json_path: str = None):
        if not json_path:
            json_path = cls._default_json_path

        with open(json_path, "r") as json_file:
            json_dict = json.load(json_file)
        return cls(json_tilt_dict=json_dict)

    def _create_graph(self, json_tilt_dict: dict,
                      parent: 'TiltNode' = None,
                      hierarchy: int = 0) -> List['TiltNode']:
        node_list = []
        edge_list = []
        sub_node_list = []
        for dict_key, dict_item in json_tilt_dict.items():
            if isinstance(dict_item, dict):
                sub_parent = self._find_parent(dict_item)
                sub_nodes, sub_edges = self._create_graph(dict_item, sub_parent,
                                                          hierarchy=hierarchy+1)
                sub_node_list.extend(sub_nodes)
                node_list.append(sub_parent)
                edge_list.extend(sub_edges)
                continue

            if isinstance(dict_item, str) and dict_key not in ["desc", "key"]:
                tilt_node = TiltNode(name=dict_item, value=None, parent=None, meta=dict_key)
                node_list.append(tilt_node)

        if parent:
            for tilt_node in node_list:
                if isinstance(tilt_node, TiltNode):
                    tilt_node.set_parent(parent)
                    edge = Edge(origin=parent.node_id,
                                target=tilt_node.node_id,
                                hierarchy=hierarchy)
                    edge_list.append(edge)
        if sub_node_list != []:
            node_list.extend(sub_node_list)
        return node_list, edge_list

    @staticmethod
    def _find_parent(json_tilt_dict: dict, value: str = None) -> 'TiltNode':
        desc = json_tilt_dict.get("desc", None)
        node = TiltNode(name=desc, value=value, parent=None)
        return node

    @staticmethod
    def _form_adjacency_matrix(edges_list: List) -> pd.DataFrame:
        colnames = set([edge.target for edge in edges_list])
        index_names = set([edge.origin for edge in edges_list])
        adjacency_matrix = pd.DataFrame(0, index=index_names, columns=colnames)
        for edge in edges_list:
            adjacency_matrix.loc[edge.origin, edge.target] = edge.hierarchy
        return adjacency_matrix

    def get_node_by_name(self, name: str = None) -> 'TiltNode':
        if name:
            node = [node for node in self.node_list if node.name == name]
            if isinstance(node, list):
                print(Warning("Multiple Nodes with the same name were found! A list will be returned."))
                return node
            return node[0]

        else:
            AttributeError("No value supplied!")

    def get_node_by_id(self, node_id: int = None) -> 'TiltNode':
        if node_id:
            return [node for node in self.node_list if node.node_id == node_id][0]
        else:
            raise AttributeError("No value supplied!")

    def get_nodes_by_ids(self, node_ids: List[int] = None) -> List['TiltNode']:
        if node_ids:
            return [node for node in self.node_list if node.node_id in node_ids]
        else:
            raise AttributeError("No value supplied!")

    def get_node_children(self, node) -> List['TiltNode']:
        child_ids = self._query_adjacency_childs(node)
        nodes = self.get_nodes_by_ids(child_ids)
        return nodes

    def _query_adjacency_childs(self, node: 'TiltNode' = None) -> List[int]:
        is_child = self.adjacency_matrix.loc[node.node_id, :] > 0
        return self.adjacency_matrix.loc[node.node_id, :][is_child].index.tolist()

    def to_dict(self) -> Dict[str, str]:
        output_dict = {}
        for adjacency_row in self.adjacency_matrix.iterrows():
            node_id = adjacency_row
            node = self.get_node_by_id(node_id)
            branch_dict = self._create_branch_dict(node)

        return NotImplementedError()

    def _create_branch_dict(self) -> Dict[str, str]:
            # node_dict = node.to_dict()
            # children = self.get_node_children(node)
            # child_dict = [child.to_dict() for child in children]
            # node_dict.update(
            #     {node.meta: child_dict}
            # )
        return NotImplementedError()


class TiltNode:
    node_id = 0

    def __init__(self, name: str = None,
                 value: str = None,
                 parent: 'TiltNode' = None,
                 meta: object = None):
        TiltNode.node_id += 1
        self.meta = meta
        self.node_id = TiltNode.node_id
        self.name = name
        self.value = value
        self.parent = parent

    def set_parent(self, parent):
        self.parent = parent

    def to_dict(self):
        return {self.name: self.value}

@dataclass
class Edge:
    origin: int
    target: int
    hierarchy: int = None


if __name__ == "__main__":
    tilt_schema = TiltSchema.create_from_json()
    node = tilt_schema.get_node_by_id(1)
    children = tilt_schema.get_node_children(node)
    print(children)
