# Flask Config from Class
class Config(object):
    SECRET_KEY = "12345678901234567890123456789012"

    MONGODB_SETTINGS = {
        'db': 'tilterdb',
        'host': "mongodb://root:SuperSecret@mongo:27017/?authSource=admin",
    }

    # Flask-User Setup
    USER_APP_NAME = "TILTer"  # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False  # Disable email authentication
    USER_ENABLE_USERNAME = True  # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = False  # Simplify register form
    USER_ENABLE_CHANGE_USERNAME = False
    USER_AFTER_LOGIN_ENDPOINT = 'member_page'