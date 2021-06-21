import uuid
from datetime import datetime
import hashlib
import json
from typing import Dict

from database.models import MetaTask


class Meta:

    def __init__(self, _id=None, name=None, version=None, language=None, created=None,
                 modified=None, url=None,
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

        self._id = _id if _id else str(uuid.uuid4())
        self.name = name
        self.created = created if created else datetime.now().isoformat()
        self.modified = modified if modified else datetime.now().isoformat()
        self.version = version if version else 1
        self.url = url
        self.language = language if language else "de"
        self.status = status if status else "active"
        self._hash = _hash if _hash else None
        self.root_task = root_task if root_task else None

    @classmethod
    def from_db_document(cls, db_document) -> 'Meta':
        """Use this method to create a Metadata class for the tilt document.
        A 'MetaTask' Object needs to be used to Instantiate this class from this
        class method. No Database Object is created with this metod.
        Afterwards the resulting object can be used for tilt creation.
        """
        cls_obj = cls(_id=db_document._id,
                      name=db_document.name,
                      created=db_document.created,
                      modified=db_document.modified,
                      version=db_document.version,
                      language=db_document.language,
                      status=db_document.status,
                      url=db_document.url,
                      root_task=db_document.root_task,
                      _hash=db_document._hash)
        return cls_obj

    def generate_hash_entry(self, tilt_dict):
        """
        Creates a Hash Value for the Meta Tilt Entry. If the Hash Value is not equal with the previous
        hash value, than the modified field will be updated as well.
        If hash values are identical, nothing happens.

        Args:
            tilt_dict ([type]): [description]
        """
        json_string = json.dumps(tilt_dict).encode('utf-8')
        new_hash = hashlib.sha256(json_string).hexdigest()
        if new_hash != self._hash:
            self.modified = datetime.now().isoformat()
            self._hash = new_hash
            print("Hash Value has been written into Metadata Object.")

    def to_tilt_dict_meta(self) -> Dict:
        tilt_dict_meta = {
            "_id": self._id,
            "name": self.name,
            "created": self.created,
            "modified": self.modified,
            "version": self.version,
            "language": self.language,
            "status": self.status,
            "url": self.url,
            "_hash": self._hash
        }
        return {"meta": tilt_dict_meta}

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
            root_task=self.root_task,
            _hash=self._hash if self._hash else None
        )
        meta_task.save()
