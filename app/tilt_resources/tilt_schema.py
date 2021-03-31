import json
import os
from typing import List, Dict, Union
from dataclasses import dataclass
import pandas as pd

from config import Config


class TiltSchema:
    # TODO: create from json - should values be stored in nodes? If yes it has to be handled over the node

    _default_json_path = os.path.join(Config.BASE_PATH, "tilt_resources/tilt_desc_mapping.json")

    def __init__(self, json_tilt_dict: dict, clean_schema: bool = True):
        """
        This class is a graph that represents a deep nested dictionary. It serves as an interface for a
        tilt document.
        On initialization the graph is created from the supplied dictionary with the function "_create_graph".
        The graph creates a node_list, adjacency_matrix and implicitly over TiltNode objects an edge_list.
        The elements of the graph serve for further operations, like retrieving nodes by names, id or
        hierarchy. The graph can also be changed into a dictionary again.

        As tilt follows a tree representation. The resulting graph can also be understood as a tree.

        Args:
            json_tilt_dict (dict): [description]
            clean_schema (bool, optional): [description]. Defaults to True.
        """
        # TODO: clean up the mess
        self.tilt_dict = json_tilt_dict
        self.edge_list = []
        self.node_list = self._create_graph(json_tilt_dict=json_tilt_dict)
        self.adjacency_matrix = self._form_adjacency_matrix(self.edge_list)
        if clean_schema:
            self._delete_all_values()

    @classmethod
    def create_from_json(cls, json_path: str = None, clean_schema: bool = False):
        """
        Creates a Tilt-Schema from a supplied json. Default path goes to the greencompany tilt document.

        Args:
            json_path (str, optional): [description]. Defaults to None.
            clean_schema (bool, optional): [description]. Defaults to False.

        Returns:
            [type]: [description]
        """
        assert json_path, "Provide a json Path, when you want to lead a tilt schema from a json file!"

        with open(json_path, "r") as json_file:
            json_dict = json.load(json_file)
        return cls(json_tilt_dict=json_dict, clean_schema=clean_schema)

    @classmethod
    def create_schema_with_desc(cls):
        """
        Loads a json with descriptions for every Tilt Entry. The descriptions are stored in the nodes and
        are used for the Tilter Frontend. So the user understands what he/she is annotating.

        Returns:
            [type]: [description]
        """

        with open(TiltSchema._default_json_path, "r") as json_file:
            json_dict = json.load(json_file)
        return cls(json_tilt_dict=json_dict)

    def _create_graph(self, json_tilt_dict: dict,
                      parent: 'TiltNode' = None,
                      hierarchy: int = 1) -> List['TiltNode']:
        """
        This is the core of the graph. This function builds the graph representation of the Tilt-Dependencies.
        The Dependencies are expressed in the form of a nested dictionary. In the repective dictionary three
        types of situations can appear.
                    1. Entries are stored in a List
                    2. Entries are stored in a dict
                    3. Entries are stored as int or string
        For all those situations the function is able to parse the respective content. For Situation 1 and 2
        sub-parents are created from the key of the current dict entry and are given into a new call of
        _create_graph together with the dict_value of the current key. Recursive execution makes the
        most sense in this case, as the depth of the dictionary is undefined. The third case works without
        recursion and just creates new nodes with the repsective edges.

        Nodes and Edges can be understood in the basic sense of graph theory. A node is a graph entry, that
        stores information, an edge connects two nodes with each other. In this case all edges are directed.
        Every edge thus defines a parent node and a child node. The Node and Edge classes are defined below.
        The creation of edges is done implicitly. Every assignment of a node as a parent, also automatically
        adds its child to the list of child in the parent node. Afterwards an edge between both nodes will be
        created in the same function call.

        Returns:
            [type]: [description]
        """
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
                    node_list.append(TiltNode(graph=self, name=dict_key,
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
        """
        Creates an adjacancy matrix. Rows are the parents columns are the childeren. Every entry in the
        adjacency matrix is a hierarchy value. As the resulting structure is a tree, every step in the tree
        is a hierarchy. So each child-parent connection also leads to a new hierarchy.

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

    def _delete_all_values(self):
        """
        Delets all values in every node.
        """
        [node.delete_value() for node in self.node_list]

    def get_nodes_from_hierachy(self, hierarchy: int = 0) -> List['TiltNode']:
        """
        Get all nodes from a specific hierarchy.

        Returns:
            [type]: [description]
        """
        node_ids = list(set([edge.origin for edge in self.edge_list if edge.hierarchy == hierarchy]))
        return self.get_nodes_by_ids(node_ids)

    def to_dict(self) -> Dict[str, str]:
        """
        Converts the graph into a dictionary representation.

        Returns:
            Dict[str, str]: [description]
        """
        output_dict = {}
        first_hierarchy_nodes = self.get_nodes_from_hierachy(1)
        for hierarchy_node in first_hierarchy_nodes:
            branch_dict = self._create_branch_dict(hierarchy_node)
            output_dict.update(branch_dict)
        return output_dict

    def _create_branch_dict(self, node) -> Dict[str, str]:
        """
        Creates a dictionary representation of a specific branch. A branch is a subgraph of the tree.
        Every subgraph, that starts at a node, which is not the root node (the node in the 0 hierarchy) is
        a branch.

        Args:
            node ([type]): [description]

        Returns:
            Dict[str, str]: [description]
        """
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
                node_dict = {**node_dict, **child_dict}
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
        """
        Defines an entry in a graph and bears information. Every node corresponts to an entry in a tilt
        document. The value of a node is the entry in the tilt document, the name of the node is the key
        in the tilt document. A node can have one parent and multiple children. If a node is assigned a parent
        it is automatically added to the childs of the parents and the creation of an edge between both is
        triggered.

        Args:
            graph (TiltSchema, optional): [description]. Defaults to None.
            name (str, optional): [description]. Defaults to None.
            desc (str, optional): [description]. Defaults to None.
            value (str, optional): [description]. Defaults to None.
            parent (TiltNode, optional): [description]. Defaults to None.
            multiple (bool, optional): [description]. Defaults to False.
            hierarchy (int, optional): [description]. Defaults to None.
        """
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
    def parent(self) -> Union['TiltNode', 'ShadowNode']:
        return self._parent

    @parent.setter
    def parent(self, parent: 'TiltNode'):
        """
        Links a node and its parent. Every time this attribute is set the current object will be added as
        child to the parent node. Adding it as a child, will trigger edge creation.

        Args:
            parent (TiltNode): [description]
        """
        if parent:
            self._parent = parent
            parent.add_children(self)
        else:
            self._parent = None

    @property
    def children(self) -> List[Union['TiltNode', 'ShadowNode']]:
        return self._children

    @children.setter
    def children(self, children: Union[List['TiltNode'], 'TiltNode']):
        """
        Sets the children of a node. Should not be used at all! Consider to delete the function.

        Args:
            children (Union[List[): [description]
        """
        if isinstance(children, list):
            edge = [Edge(self.node_id, child.node_id, hierarchy=self.hierarchy)
                    for child in children]
        else:
            edge = [Edge(origin=self.node_id, target=children.node_id, hierarchy=self.hierarchy)]
        self._children = children
        self.graph.edge_list.extend(edge)

    def add_children(self, children: Union[List[Union['TiltNode', 'ShadowNode']], 'TiltNode', 'ShadowNode']):
        """
        Adds children to the node. Children are a List of Nodes or just single Nodes. Every new children
        creates a new edge in the graph.

        Args:
            children (Union[List[): [description]
        """
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
        """
        A node that serves as a Helper to combine list entries. E.g.:
            "legalBases": [
          {
            "reference": "",
            "description": "Data Disclosed - Legal Basis"
          },
          {
            "reference": "",
            "description": ""
          }
        ]
        For each entry that is an iterator a shadownode will be created. The node does not have an edges
        connected it directly with other nodes. The edges which are created, will be forwarded to the parent
        of the shadownode. The only reference that reveal the true connects are stored in the child and parent
        attributes of the respective nodes. This is to avoid confusion in the adjacency matrix.

        Args:
            name (str, optional): [description]. Defaults to None.
            value (str, optional): [description]. Defaults to None.
            parent (TiltNode, optional): [description]. Defaults to None.
            graph (TiltSchema, optional): [description]. Defaults to None.
            hierarchy (int, optional): [description]. Defaults to None.
        """
        super().__init__(name=name, value=value, graph=graph, hierarchy=hierarchy)
        assert parent, "A ShadowNode needs a Parent on initialization!"
        self.parent = parent

    def add_children(self, children: 'TiltNode'):
        """
        On child creation. An edge will not connect with the shadow node. The origin of the edge is forwarded
        to the parent of the shadownode.

        Args:
            children (TiltNode): [description]
        """
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
    """
    An directed edge of a graph, which goes from one node to another.
    """
    origin: int
    target: int
    hierarchy: int = None


if __name__ == "__main__":
    json_path = os.path.join(Config.ROOT_PATH, "data/test_data/tilt_schema.json")
    tilt_schema = TiltSchema.create_from_json(json_path=json_path)
    node = tilt_schema.get_node_by_id(1)
    children = node.children
    tilt_dict = tilt_schema.to_dict()
    test_json_path = os.path.join(Config.ROOT_PATH, "data/test_data/test_tilt_schema.json")
    with open(test_json_path, "w") as f:
        json.dump(tilt_dict, f)
    print(tilt_dict == tilt_schema.tilt_dict)
