import uuid
from datetime import datetime
import hashlib
import json

from database.models import MetaTask


class Meta:

    def __init__(self, version=None, language=None, created=None,
                 root_task=None, status=None, _hash=None):
        """This class is a wrapper to a MongoEngine Document Class.
        The wrapper is the Metadata Object which gets written into the Tilt Document.
        It automatically passes necessary information for persistance to the document
        class. In Tilt Creation this objet is reinstatiated again to prepare it for writing
        it into the tilt document.

        Args:
            version ([type], optional): [description]. Defaults to None.
            language ([type], optional): [description]. Defaults to None.
        """
        self._id = uuid.uuid4()
        self.created = created if created else datetime.now().isoformat()
        self.modified = datetime.now().isoformat()
        self.version = version if version else 1
        self.language = language if language else "de"
        self.status = status if status else "active"
        self._hash = _hash if _hash else None
        self.root_task = root_task if root_task else None

    @classmethod
    def from_db_document(cls, db_document):
        """Use this method to create a Metadata class for the tilt document.
        A 'MetaTask' Object needs to be used to Instantiate this class from this
        class method. No Database Object is created with this metod. Afterwards the resulting object can be used for tilt creation.
        """
        cls_obj = cls(_id=db_document._id,
                      created=db_document.created,
                      version=db_document.version,
                      language=db_document.language,
                      status=db_document.status,
                      root_task=db_document.root_task)
        return cls_obj

    @property
    def _hash(self):
        if self._hash_:
            return self._hash
        else:
            raise AttributeError("Can get _hash. No Hash Value created yet!")

    @_hash.setter
    def _hash(self, value):
        if self._hash_ and self._hash_ != value:
            self.modified = datetime.now().isotime()
        self._hash_ = value

    def generate_hash_value(self, tilt_dict):
        json_string = json.dumps(tilt_dict).encode('uft-8')
        self._hash = hashlib.sha256(json_string).hexdigest()
        print("Hash Value has been written into Metadata Object.")

    def to_tilt_dict_meta(self):
        tilt_dict_meta = {
            "_id": self._id,
            "name": self.name,
            "created": self.created,
            "modified": self.modified,
            "version": self.version,
            "language": self.language,
            "status": self.status,
            "url": self.url,
            "_hash": self.hash
        }
        return tilt_dict_meta

    def save(self):
        meta_task = MetaTask(
            _id=self._id,
            name=self.name,
            created=self.created,
            modified=self.modified,
            version=self.version,
            language=self.language,
            status=self.status,
            url=self.url,
            root_task=self.root_task
        )
        meta_task.save()
