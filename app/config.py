import json


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

    with open('secrets/secrets.json') as f:
        data = json.load(f)
        SECRET_KEY = data["flask_secret_key"]
        MONGODB_SETTINGS = {"db": data["mongodb_database"],
                            "host": f"mongodb://{data['mongodb_user']}:{data['mongodb_password']}"
                                    f"@mongo:{data['mongodb_port']}/?authSource=admin"}