from dataclasses import dataclass
from config import Config
from typing import Dict, Union


@dataclass
class TiltException:
    schema_key_queue: list = None
    tilt_exception_entry: Union[int, str] = None

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
        self._read_tilt_exceptions_from_config(Config)

    def add_tilt_exception(self, tilt_exception: 'TiltException'):
        self.tilt_exceptions.append(tilt_exception)

    def _read_tilt_exceptions_from_config(self, config: Config):
        tilt_exception_list = config.TILT_EXCEPTIONS
        for tilt_exception_kw in tilt_exception_list:
            tilt_exception_obj = TiltException(**tilt_exception_kw)
            self.add_tilt_exception(tilt_exception_obj)

    def write_tilt_default_values(self) -> Dict:
        for tilt_exception in self.tilt_exceptions:
            updated_tilt_document = self._place_default_values(tilt_exception, self.tilt_document)
            self.tilt_document = updated_tilt_document

    def _place_default_values(self, tilt_exception: 'TiltException', tilt_document: Dict = None):
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
