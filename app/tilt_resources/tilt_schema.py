import json
import os
from typing import List, Dict, Union
from dataclasses import dataclass
import pandas as pd

from config import Config


class TiltSchema:

    _default_json_path = os.path.join(Config.BASE_PATH, "tilt_resources/tilt_schema.json")

    def __init__(self, json_tilt_dict: dict, clean_schema: bool = True):
        """
        This class is a graph representation of a supplied json file.
        The schems is used for tilt-documents.

        Args:
            json_tilt_dict (dict): [description]
            clean_schema (bool, optional): [description]. Defaults to True.
        """
        self.tilt_dict = json_tilt_dict
        self.edge_list = []
        self.node_list = self._create_graph(json_tilt_dict=json_tilt_dict)
        self.adjacency_matrix = self._form_adjacency_matrix(self.edge_list)
        if clean_schema:
            self.delete_all_values()

    @classmethod
    def create_from_json(cls, json_path: str = None, clean_schema: bool = False):
        if not json_path:
            json_path = cls._default_json_path

        with open(json_path, "r") as json_file:
            json_dict = json.load(json_file)
        return cls(json_tilt_dict=json_dict, clean_schema=clean_schema)

    @classmethod
    def create_schema_with_desc(cls):
        desc_json_path = os.path.join(Config.BASE_PATH, "tilt_resources/desc_mapping.json")
        with open(desc_json_path, "r") as json_file:
            json_dict = json.load(json_file)
        return cls(json_tilt_dict=json_dict)

    def _create_graph(self, json_tilt_dict: dict,
                      parent: 'TiltNode' = None,
                      hierarchy: int = 1) -> List['TiltNode']:
        node_list = []
        sub_node_list = []
        for dict_key, dict_item in json_tilt_dict.items():
            if isinstance(dict_item, list):
                node_list_entries = []
                sub_parent = TiltNode(graph=self, name=dict_key, multiple=True, hierarchy=hierarchy,
                                      parent=parent)
                node_list.append(sub_parent)
                for list_entry in dict_item:
                    if isinstance(list_entry, dict):
                        shadow_parent = ShadowNode(name='', parent=sub_parent, graph=self,
                                                   hierarchy=hierarchy)
                        sub_nodes = self._create_graph(list_entry, shadow_parent,
                                                       hierarchy=hierarchy+1)
                        sub_node_list.extend(sub_nodes)
                    else:
                        node_list_entries.append(list_entry)
                if node_list_entries != []:
                    node_list.append(TiltNode(graph=self, name=dict_key, value=node_list_entries,
                                              parent=parent,
                                              hierarchy=hierarchy,
                                              desc=node_list_entries))
                continue
            if isinstance(dict_item, dict):
                sub_parent = TiltNode(graph=self, name=dict_key, hierarchy=hierarchy, parent=parent)
                sub_nodes = self._create_graph(dict_item, sub_parent,
                                               hierarchy=hierarchy+1)
                sub_node_list.extend(sub_nodes)
                node_list.append(sub_parent)
                continue

            if isinstance(dict_item, str) or isinstance(dict_item, int):
                tilt_node = TiltNode(graph=self, name=dict_key,
                                     parent=parent, hierarchy=hierarchy, desc=dict_item)
                node_list.append(tilt_node)
        if sub_node_list != []:
            node_list.extend(sub_node_list)
        return node_list

    @staticmethod
    def _form_adjacency_matrix(edges_list: List) -> pd.DataFrame:
        """Creates an adjacancy matrix. Rows are the parents columns are the childeren.

        Args:
            edges_list (List): [description]

        Returns:
            pd.DataFrame: [description]
        """
        colnames = set([edge.target for edge in edges_list])
        index_names = set([edge.origin for edge in edges_list])
        adjacency_matrix = pd.DataFrame(0, index=index_names, columns=colnames)
        for edge in edges_list:
            adjacency_matrix.loc[edge.origin, edge.target] = edge.hierarchy
        return adjacency_matrix

    def get_node_by_name(self, name: str = None) -> 'TiltNode':
        if name:
            node = [node for node in self.node_list if node.name == name]
            if len(node) > 1:
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
        return [node for node in self.node_list if node.node_id in node_ids]

    def delete_all_values(self):
        [node.delete_value() for node in self.node_list]

    def get_nodes_from_hierachy(self, hierarchy: int = 0) -> List['TiltNode']:
        node_ids = list(set([edge.origin for edge in self.edge_list if edge.hierarchy == hierarchy]))
        return self.get_nodes_by_ids(node_ids)

    def to_dict(self) -> Dict[str, str]:
        output_dict = {}
        first_hierarchy_nodes = self.get_nodes_from_hierachy(1)
        for hierarchy_node in first_hierarchy_nodes:
            branch_dict = self._create_branch_dict(hierarchy_node)
            output_dict.update(branch_dict)
        return output_dict

    def _create_branch_dict(self, node) -> Dict[str, str]:
        if node._multiple:
            node_dict = {node.name: []}
        elif isinstance(node, ShadowNode):
            node_dict = {}
        else:
            node_dict = {node.name: {}}
        for child in node.children:
            child_dict = self._create_branch_dict(child)
            if node._multiple:
                node_dict[node.name].append(child_dict)
            elif isinstance(node, ShadowNode):
                node_dict = node_dict | child_dict
            else:
                node_dict[node.name].update(child_dict)
        if not node.children:
            node_dict.update(node.to_dict())
        return node_dict


class TiltNode:
    node_id = 0

    def __init__(self,
                 graph: 'TiltSchema' = None,
                 name: str = None,
                 desc: str = None,
                 value: str = None,
                 parent: 'TiltNode' = None,
                 multiple: bool = False,
                 hierarchy: int = None):
        self.graph = graph
        assert self.graph, "A Node needs a Graph!"
        TiltNode.node_id += 1
        self.node_id = TiltNode.node_id
        assert hierarchy is not None, "A Node needs a Hierarchy!"
        self.hierarchy = hierarchy
        self.name = name
        self.value = value
        self.parent = parent
        self._multiple = multiple
        self.children = []
        self.desc = desc

    def to_dict(self):
        return {self.name: self.value}

    def delete_value(self):
        self.value = None

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent: 'TiltNode'):
        if parent:
            edge = Edge(origin=parent.node_id, target=self.node_id, hierarchy=self.hierarchy)
            self.graph.edge_list.append(edge)
            self._parent = parent
            parent.add_children(self)
        else:
            self._parent = None

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, children: Union[List['TiltNode'], 'TiltNode']):
        if isinstance(children, list):
            edge = [Edge(self.node_id, child.node_id, hierarchy=self.hierarchy)
                    for child in children]
        else:
            edge = [Edge(origin=self.node_id, target=self.node_id, hierarchy=self.hierarchy)]
        self._children = children
        self.graph.edge_list.extend(edge)

    def add_children(self, children: Union[List['TiltNode'], 'TiltNode']):
        if isinstance(children, list):
            edge = [Edge(self.node_id, child.node_id, hierarchy=self.hierarchy)
                    for child in children]
            self._children.extend(children)
        else:
            edge = [Edge(origin=self.node_id, target=children.node_id, hierarchy=self.hierarchy)]
            self._children.append(children)
        self.graph.edge_list.extend(edge)

    def set_value(self, value):
        self.value = value


class ShadowNode(TiltNode):

    def __init__(self, name: str = None,
                 value: str = None,
                 parent: 'TiltNode' = None,
                 graph: 'TiltSchema' = None,
                 hierarchy: int = None):
        super().__init__(name=name, value=value, graph=graph, hierarchy=hierarchy)
        assert parent, "A ShadowNode needs a Parent on initialization!"
        self.parent = parent

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent: 'TiltNode'):
        if parent:
            self._parent = parent
            parent.add_children(self)
        else:
            self._parent = None

    def add_children(self, children: 'TiltNode'):
        if isinstance(children, list):
            edge = [Edge(self.parent.node_id, target=child.node_id, hierarchy=self.hierarchy)
                    for child in children]
            self._children.extend(children)
        else:
            edge = [Edge(origin=self.parent.node_id, target=children.node_id, hierarchy=self.hierarchy)]
            self._children.append(children)
        self.graph.edge_list.extend(edge)


@dataclass
class Edge:
    origin: int
    target: int
    hierarchy: int = None


if __name__ == "__main__":
    tilt_schema = TiltSchema.create_from_json()
    node = tilt_schema.get_node_by_id(1)
    children = node.children
    tilt_dict = tilt_schema.to_dict()
    test_json_path = os.path.join(Config.BASE_PATH, "tilt_resources/test_tilt_schema.json")
    with open(test_json_path, "w") as f:
        json.dump(tilt_dict, f)
    print(tilt_dict == tilt_schema.tilt_dict)
