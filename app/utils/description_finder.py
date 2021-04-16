from typing import Dict, List
from config import Config
import json
from database.models import Task
from tilt_resources.tilt_schema import TiltNode, TiltSchema


class DescriptonFinder:

    tilt_dict = Config.TILT_DICT

    def __init__(self) -> None:

        """
        Finds all necessary descriptions for a provided task.
        As tasks are created over the schema.json, names for potential annotations of a task are mapped from
        schema.json into the Tiltschema. The TiltSchema gives a representation of an actual tilt document and
        has the appropriate keys to navigate through the tilt_desc.json.
        The keys for navigation are retrieved over the nodes in TiltSchema, as nodes store their path in the
        graph. Over conditionals those keys are used to navigate through tilt_desc.json.
        """
        with open(Config.DESC_PATH, "r") as json_file:
            self.tilt_descriptions = json.load(json_file)
        tilt_schema = TiltSchema.create_schema_with_desc()
        # mappings are required to be unique
        self.schema_to_tilt_mapping = self._create_schema_to_tilt_mapping(tilt_schema)

    def _get_path_node_names(self, label: str) -> List[str]:
        """Get label_chain of a node. The label chain is the node path in the graph, whereas every path entry
        is a node.name argument. Empty names from ShadowNodes are ignored.

        Args:
            label (str): [description]

        Returns:
            [type]: [description]
        """
        node = self.schema_to_tilt_mapping[label]
        label_chain = [path_node.name for path_node in node.path if path_node.name != '']
        return label_chain

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
            description = self._find_description_by_label_chain(label_chain, tilt_entry)
        else:
            description = tilt_dict["description"]
        return description

    def find_descriptions(self, task: 'Task') -> Dict[str, str]:
        """
        Finds all descriptions for a provided task and returns these discriptions in a dictionary.
        Key = Label_name
        Value = Description

        Args:
            task (Task): [description]

        Returns:
            Dict[str, str]: [description]
        """
        label_descriptions = {}
        for label in task.labels:
            label_chain = self._get_path_node_names(label)
            label_descriptions[label] = self._find_description_by_label_chain(
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
                desc = self._get_entry_from_tilt_dict(label=label, tilt_dict=desc)
        return desc

    @staticmethod
    def _create_schema_to_tilt_mapping(tilt_schema: TiltSchema) -> Dict[str, TiltNode]:
        """
        Creates a unique mapping from schema.json to the tilt_schema nodes.
        If the nodes do not have unique 'desc' entries the mapping will not be created and throw an error.

        Args:
            tilt_schema (TiltSchema): [description]

        Raises:
            AttributeError: [description]

        Returns:
            Dict: [description]
        """
        schema_to_tilt_mapping = {}
        for node in tilt_schema:
            if schema_to_tilt_mapping.get(node.desc):
                raise AttributeError("Schema to Tilt Mapping is not unique!")
            elif not schema_to_tilt_mapping.get(node.desc) and node.desc:
                schema_to_tilt_mapping[node.desc] = node
        return schema_to_tilt_mapping
