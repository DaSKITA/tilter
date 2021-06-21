from config import Config
from typing import Dict, Union, List


class TiltException:
    """
    A class for storing tilt exceptions. Every exceptions contains a schema_key_queue and a
    tilt_exception entry. The schema_key_queue is a path through the tilt_document. The tilt_exception_entry
    is the default value, for the given path in the schema_key_queue.

    Returns:
        [type]: [description]
    """
    def __init__(self, schema_key_queue: List = None, tilt_exception_entry: Union[str, int] = None) -> None:
        if schema_key_queue:
            self.schema_key_queue = list(schema_key_queue)
        else:
            self.schema_key_queue = []

        if tilt_exception_entry:
            self.tilt_exception_entry = tilt_exception_entry
        else:
            self.tilt_exception_entry = None

    def _queue_is_empty(self):
        return self.schema_key_queue == []


class TiltCreator:
    """
    This class is for creating tilt documents. Currently it just supports placing default values.
    In future this might change.
    """

    def __init__(self, tilt_document: Dict = None) -> None:
        self.tilt_exceptions = []
        if tilt_document:
            # TODO: once the class creates a tilt document on its own, this option has to go
            self.tilt_document = tilt_document
        else:
            self.tilt_document = {}
        self.tilt_exception_obj_list = self._read_tilt_exceptions_from_config(Config)

    def add_tilt_exception(self, tilt_exception: 'TiltException'):
        self.tilt_exceptions.append(tilt_exception)

    def _read_tilt_exceptions_from_config(self, config: Config):
        tilt_exception_list = config.TILT_EXCEPTIONS
        tilt_exception_obj_list = []
        for tilt_exception_kw in tilt_exception_list:
            tilt_exception_obj = TiltException(**tilt_exception_kw)
            tilt_exception_obj_list.append(tilt_exception_obj)
        return tilt_exception_obj_list

    def write_tilt_default_values(self) -> Dict:
        """
        Iterates over exception classes to retrieve default values. Every default value is written in the
        config.py. Every iteration the tilt document stored in the class variables in updated.

        Returns:
            Dict: [description]
        """
        for tilt_exception in self.tilt_exception_obj_list:
            updated_tilt_document = self._place_default_values(tilt_exception, self.tilt_document)
            self.tilt_document = updated_tilt_document

    def _place_default_values(self, tilt_exception: 'TiltException', tilt_document: Dict = None) -> Dict:
        """
        Iterates through a given tilt_document recursively. Based in the type of the retrieved entry another
        recursive call is triggered or the existinng value in the exception class is added under the
        respective key. Iteration is basically done over a "schema_key_queue", which is a list full of
        labels from the tilt schema. This list can be seen as a path through the tilt_document.

        Args:
            tilt_exception (TiltException): [description]
            tilt_document (Dict, optional): [description]. Defaults to None.

        Returns:
            Dict: [description]
        """
        schema_key = tilt_exception.schema_key_queue.pop(0)
        if isinstance(tilt_document, list):
            for idx, _ in enumerate(tilt_document):
                if tilt_exception._queue_is_empty():
                    if not tilt_document[idx].get(schema_key):
                        tilt_document[idx][schema_key] = tilt_exception.tilt_exception_entry
                else:
                    tilt_document[idx][schema_key] = self._place_default_values(
                        tilt_exception=tilt_exception,
                        tilt_document=tilt_document[idx][schema_key])
        else:
            if tilt_exception._queue_is_empty():
                if not tilt_document.get(schema_key):
                    tilt_document[schema_key] = tilt_exception.tilt_exception_entry
            else:
                tilt_document[schema_key] = self._place_default_values(
                    tilt_exception=tilt_exception,
                    tilt_document=tilt_document[schema_key])
        return tilt_document

    def get_tilt_document(self):
        return self.tilt_document
