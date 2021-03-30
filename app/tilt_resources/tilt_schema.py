"This is just a first scetch, in case task creatinon should be changed"
import json
import os
from typing import List, Dict, Union
from dataclasses import dataclass
import pandas as pd

from config import Config


class TiltSchema:

    _default_json_path = os.path.join(Config.BASE_PATH, "tilt_resources/tilt_schema.json")

    def __init__(self, json_tilt_dict: dict, clean_schema: bool = True):
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

    def _create_graph(self, json_tilt_dict: dict,
                      parent: 'TiltNode' = None,
                      hierarchy: int = 0) -> List['TiltNode']:
        node_list = []
        sub_node_list = []
        for dict_key, dict_item in json_tilt_dict.items():
            if isinstance(dict_item, list):
                node_list_entries = []
                sub_parent = TiltNode(graph=self, name=dict_key, multiple=True, hierarchy=hierarchy)
                node_list.append(sub_parent)
                for list_entry in dict_item:
                    if isinstance(list_entry, dict):
                        sub_nodes = self._create_graph(list_entry, sub_parent,
                                                       hierarchy=hierarchy+1)
                        sub_node_list.extend(sub_nodes)
                    else:
                        node_list_entries.append(list_entry)
                if node_list_entries != []:
                    node_list.append(TiltNode(graph=self, name=dict_key, value=node_list_entries,
                                              hierarchy=hierarchy))
                continue
            if isinstance(dict_item, dict):
                sub_parent = TiltNode(graph=self, name=dict_key, hierarchy=hierarchy)
                sub_nodes = self._create_graph(dict_item, sub_parent,
                                               hierarchy=hierarchy+1)
                sub_node_list.extend(sub_nodes)
                node_list.append(sub_parent)
                continue

            if isinstance(dict_item, str) or isinstance(dict_item, int):
                tilt_node = TiltNode(graph=self, name=dict_key, value=dict_item,
                                     parent=parent, hierarchy=hierarchy)
                parent.add_children(tilt_node)
                node_list.append(tilt_node)

        if sub_node_list != []:
            node_list.extend(sub_node_list)
        return node_list

    @staticmethod
    def _form_adjacency_matrix(edges_list: List) -> pd.DataFrame:
        """Creates am adjacancy matrix. Rows are the parents columns are the childeren.

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

    def get_node_children(self, node) -> List['TiltNode']:
        child_ids = self._query_adjacency_childs(node)
        child_nodes = self.get_nodes_by_ids(child_ids)
        return child_nodes

    def _query_adjacency_childs(self, node: 'TiltNode' = None) -> List[int]:
        if node.node_id in self.adjacency_matrix.index:
            is_child = self.adjacency_matrix.loc[node.node_id, :] > 0
            children = self.adjacency_matrix.loc[node.node_id, :][is_child].index.tolist()
        else:
            children = []
        return children

    def delete_all_values(self):
        [node.delete_value() for node in self.node_list]

    def get_nodes_from_hierachy(self, hierarchy: int = 0) -> List['TiltNode']:
        is_hierarchy_x = (self.adjacency_matrix == hierarchy).index
        node_ids = self.adjacency_matrix.loc[is_hierarchy_x, :].index.tolist()
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
        else:
            node_dict = {node.name: {}}
        children = self.get_node_children(node)
        for child in children:
            child_dict = self._create_branch_dict(child)
            if node._multiple:
                node_dict[node.name].append(child_dict)
            else:
                node_dict[node.name].update(child_dict)
        if not children:
            node_dict.update(node.to_dict())
        return node_dict


class TiltNode:
    node_id = 0

    def __init__(self,
                 graph: 'TiltSchema' = None,
                 name: str = None,
                 value: str = None,
                 parent: 'TiltNode' = None,
                 multiple: bool = False,
                 children: 'TiltNode' = None,
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
        if not children:
            self.children = []
        else:
            self.children = children

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
            edge = [Edge(origin=self.node_id, target=self.node_id, hierarchy=self.hierarchy)]
            self._children.append(children)
        self.graph.edge_list.extend(edge)


class ShadowNode(TiltNode):

    def __init__(self, name: str = None,
                 value: str = None,
                 parent: 'TiltNode' = None,
                 multiple: bool = False):
        super().__init__(name=name, value=value, parent=parent, multiple=multiple)


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
