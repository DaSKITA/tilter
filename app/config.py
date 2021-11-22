import os
from pathlib import Path
import json


# Flask Config from Class
class Config(object):

    # Secrets
    BASE_PATH = os.path.abspath(os.path.dirname(__file__))
    DEPLOYMENT = os.environ.get("DEPLOYMENT", False)
    LOCAL_HOST = "http://127.0.0.1/"

    # Flask-User Setup
    USER_APP_NAME = "TILTer"  # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False  # Disable email authentication
    USER_ENABLE_USERNAME = True  # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = False  # Simplify register form
    USER_ENABLE_CHANGE_USERNAME = False
    USER_AFTER_LOGIN_ENDPOINT = 'tasks'

    JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
    JWT_HEADER_TYPE = ""

    LANGUAGES = ['en', 'de']

    ROOT_PATH = Path(BASE_PATH).parent
    TEST_PATH = os.path.join(ROOT_PATH, "test")
    DESC_PATH = os.path.join(BASE_PATH, "tilt_resources/tilt_desc.json")
    SCHEMA_PATH = os.path.join(BASE_PATH, "tilt_resources/schema.json")
    COMPLETE_SCHEMA_PATH = os.path.join(BASE_PATH, 'tilt_resources/tilt-complete-schema.json')

    with open(SCHEMA_PATH, 'r') as json_file:
        SCHEMA_DICT = json.load(json_file)

    with open(COMPLETE_SCHEMA_PATH, 'r') as complete_schema_file:
        COMPLETE_SCHEMA = json.load(complete_schema_file)

    SECRET_KEY = os.environ["FLASK_SECRET_KEY"]
    POLICY_DIR = os.path.join(ROOT_PATH, "data/official_policies") if DEPLOYMENT \
        else os.path.join(ROOT_PATH, "data/test_policies")

    def _create_mongo_settings(mongodb_user: str,
                               mongodb_password: str,
                               mongodb_port: str,
                               mongodb_database: str,
                               host: str) -> str:
        host = f"mongodb://{mongodb_user}:{mongodb_password}" + \
            f"@{host}:{mongodb_port}/{mongodb_database}?authSource=admin"
        return {"host": host}

    MONGODB_SETTINGS = _create_mongo_settings(mongodb_user=os.environ["MONGODB_USERNAME"],
                                              mongodb_password=os.environ["MONGODB_PASSWORD"],
                                              mongodb_port=os.environ["MONGODB_PORT"],
                                              mongodb_database=os.environ["MONGO_INITDB_DATABASE"],
                                              host=os.environ.get("MONGODB_HOST", "localhost"))

    TILT_EXCEPTIONS = [
        {
            "schema_key_queue": ["dataDisclosed", "storage", "aggregationFunction"],
            "tilt_exception_entry": "max"
        }
    ]
