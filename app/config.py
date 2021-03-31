from dotenv import load_dotenv
import os
from pathlib import Path


# Flask Config from Class
class Config(object):

    # Flask-User Setup
    USER_APP_NAME = "TILTer"  # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False  # Disable email authentication
    USER_ENABLE_USERNAME = True  # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = False  # Simplify register form
    USER_ENABLE_CHANGE_USERNAME = False
    USER_AFTER_LOGIN_ENDPOINT = 'member_page'

    LANGUAGES = ['en', 'de']

    BASE_PATH = os.path.abspath(os.path.dirname(__file__))
    ROOT_PATH = Path(BASE_PATH).parent
    TEST_PATH = os.path.join(ROOT_PATH, "test")

    # Secrets
    if not os.environ.get("DEPLOYMENT", None):
        load_dotenv(dotenv_path=os.path.join(BASE_PATH, "secrets/local/flask-local.env"))

    SECRET_KEY = os.environ["FLASK_SECRET_KEY"]

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
                                              mongodb_database=os.environ["MONGODB_DATABASE"],
                                              host=os.environ.get("MONGODB_HOST", "localhost"))
