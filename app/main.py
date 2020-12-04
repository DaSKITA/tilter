from flask import Flask, render_template, render_template_string
from flask_mongoengine import MongoEngine
from flask_user import login_required, UserManager, UserMixin


# Flask Config from Class
class ConfigClass(object):
    SECRET_KEY = "unsecure_test_key_which_is_still_32_bytes_long"

    MONGODB_SETTINGS = {
        'db': 'tilterdb',
        'host': "mongodb://root:SuperSecret@mongo:27017/?authSource=admin",
    }

    # Flask-User Setup
    USER_APP_NAME = "TILTer"  # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False  # Disable email authentication
    USER_ENABLE_USERNAME = True  # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = False  # Simplify register form


# Flask App
app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')

# MongoDB Setup
db = MongoEngine()
db.init_app(app)


# Model Entries
class Task(db.Document):
    name = db.StringField(max_length=255)
    label = db.DictField()
    interfaces = db.ListField()
    text = db.StringField()


class User(db.Document, UserMixin):
    active = db.BooleanField(default=True)

    # User authentication information
    username = db.StringField(default='', max_length=16)
    password = db.StringField(min_length=6)

    # User information
    first_name = db.StringField(default='', max_length=255)
    last_name = db.StringField(default='', max_length=255)

    # Relationships
    roles = db.ListField(db.StringField(), default=[])


# Setup Flask-User and specify the User data-model
user_manager = UserManager(app, db, User)


class Annotation(db.Document):
    from_user = db.ReferenceField('User', required=True)


# Filling DB with test data
# Task(name="IMDB", label={"Controller": "blue", "Organization": "red"},
#      interfaces=[
#          "panel",
#          "update",
#          "controls",
#          "side-column",
#          "completions:menu",
#          "completions:add-new",
#          "completions:delete",
#          "predictions:menu"],
#      text="IMDb Privacy Notice <br><br>|||Last Updated, December 5, 2014 . To see what has changed click here. <br><br>|||IMDb knows that you care how information about you is used and shared, and we appreciate your trust that we will do so carefully and sensibly. <br><br>|||By visiting IMDb, you are accepting the practices described in this Privacy Notice. <br><br>|||<strong> What Personal Information About Users Does IMDb Gather- </strong><br><br> The information we learn from users helps us personalize and continually improve your experience at IMDb. Here are the types of information we gather. <br><br>|||<strong> Information You Give Us : </strong> We receive and store any information you enter on our Web site or give us in any other way. Click here to see examples of what we collect. You can choose not to provide certain information, but then you might not be able to take advantage of many of our features. We use the information that you provide for such purposes as responding to your requests, customizing future browsing for you, improving our site, and communicating with you. <br><br>|||<strong> Automatic Information : </strong> We receive and store certain types of information whenever you interact with us. For example, like many Web sites, we use \"cookies,\" and we obtain certain types of information when your Web browser accesses IMDb or advertisements and other content served by or on behalf of IMDb on other Web sites. Click here to see examples of the information we receive. <br><br>|||<strong> E-mail Communications : </strong> To help us make e-mails more useful and interesting, we often receive a confirmation when you open e-mail from IMDb if your computer supports such capabilities. We also compare our user list to lists received from other companies, in an effort to avoid sending unnecessary messages to our users. If you do not want to receive e-mail or other mail from us, please use our User Administration pages to adjust your preferences. <br><br>|||<strong> Mobile : </strong> When you download or use apps created by IMDb, we may receive information about your location and your mobile device, including a unique identifier for your device. We may use this information to provide you with location-based services, such as advertising, local showtimes, search results, and other personalized content. Most mobile devices allow you to turn off location services. For more information about how to do this, click here. <br><br>|||<strong> Information from Other Sources : </strong> We might receive information about you from other sources and add it to our account information. Click here to see examples of the information we receive. <br><br>|||<strong> What About Cookies- </strong><br><br><ul><li> Cookies are alphanumeric identifiers that we transfer to your computer's hard drive through your Web browser to enable our systems to recognize your browser and to provide features such as My Movies, local show times, and browsing preferences. </ul></li>|||<ul><li> The \"help\" portion of the toolbar on most browsers will tell you how to prevent your browser from accepting new cookies, how to have the browser notify you when you receive a new cookie, or how to disable cookies altogether. Additionally, you can disable or delete similar data used by browser add-ons, such as Flash cookies, by changing the add-on's settings or visiting the Web site of its manufacturer. However, because cookies allow you to take full advantage of some of IMDb's essential features, we recommend that you leave them turned on. </ul></li>|||<ul><li> We use web beacons (also known as \"action tags\" or \"single-pixel gifs\") and other technologies to measure the effectiveness of certain site features and to conduct research and analysis. We also allow third parties to place web beacons and other technologies on our site to conduct research and analysis, but we do not provide personal information to such third parties. </ul></li>|||<strong> Does IMDb Share the Information It Receives- </strong><br><br> Information about our users is an important part of our business, and we are not in the business of selling it to others. We share user information with our parent corporation (Amazon.com, Inc.), the subsidiaries it controls, and as described below. <br><br>|||<strong> Affiliated Businesses We Do Not Control : </strong> We work closely with our affiliated businesses. In some cases, we will include offerings from these businesses on IMDb. In other cases, we may include joint offerings from IMDb and these businesses on IMDb. You can tell when another business is involved in the offering, and we share user information related to those offerings with that business. <br><br>|||<strong> Agents : </strong> We employ other companies and individuals to perform functions on our behalf. Examples include sending e-mail, removing repetitive information from user lists, analyzing data, and providing marketing assistance. They have access to personal information needed to perform their functions, but may not use it for other purposes. <br><br>|||<strong> Promotional Offers : </strong> Sometimes we send offers to selected groups of IMDb users on behalf of other businesses. When we do this, we do not give that business your name and e-mail address. If you do not want to receive such offers, please use our User Administration pages to adjust your preferences. <br><br>|||<strong> Business Transfers : </strong> As we continue to develop our business, we might sell or buy additional services or business units. In such transactions, user information generally is transferred along with the rest of the service or business unit. Also, in the event that IMDb, Inc., or substantially all of its assets are acquired, user information will of course be included in the transaction. <br><br>|||<strong> Protection of IMDb and Others : </strong> We release account and other personal information when we believe release is appropriate to comply with law; enforce or apply our Terms and Conditions of Use and other agreements; or protect the rights, property, or safety of IMDb, our users, or others. This includes exchanging information with other companies and organizations for fraud protection and credit risk reduction. Obviously, however, this does not include selling, renting, sharing, or otherwise disclosing personally identifiable information from customers for commercial purposes in violation of the commitments set forth in this Privacy Notice. <br><br>|||<strong> With Your Consent : </strong> Other than as set out above, you will always receive notice when information about you might go to third parties, and you will have an opportunity to choose not to share the information. <br><br><strong> What About Third-Party Advertisers- </strong><br><br> Our site includes third-party advertising and links to other websites. We do not provide any personally identifiable customer information to these advertisers or third-party websites. <br><br>|||These third-party websites and advertisers, or Internet advertising companies working on their behalf, sometimes use technology to send (or \"serve\") the advertisements that appear on our website directly to your browser. They automatically receive your IP address when this happens. They may also use cookies, JavaScript, web beacons (also known as action tags or single-pixel gifs), and other technologies to measure the effectiveness of their ads and to personalize advertising content. We do not have access to or control over cookies or other features that they may use, and the information practices of these advertisers and third-party websites are not covered by this Privacy Notice. Please contact them directly for more information about their privacy practices. In addition, the Network Advertising Initiative offers useful information about Internet advertising companies (also called \"ad networks\" or \"network advertisers\"), including information about how to opt-out of their information collection. <br><br>|||IMDb also displays personalized third-party advertising based on personal information about users, such as information you submit to us about movies you own or have watched. Click here for more information about the personal information that we gather. Although IMDb does not provide any personal information to advertisers, advertisers (including ad-serving companies) may assume that users who interact with or click on a personalized advertisement meet their criteria to personalize the ad (for example, users in the northwestern United States who bought, watched, or browsed for romantic comedies). If you do not want us to use personal information that we gather to allow third parties to personalize advertisements we display to you, please adjust your Advertising Preferences. <br><br>|||<strong> How Secure Is Information About Me- </strong><br><br> If you use our subscription service, we work to protect the security of your subscription information during transmission by using Secure Sockets Layer (SSL) software, which encrypts information you input. <br><br>|||It is important for you to protect against unauthorized access to your password and to your computer. Be sure to sign off when finished using a shared computer. <br><br>|||<strong> What Choices and Access Do I Have- </strong><br><br><ul><li> As discussed above, you can always choose not to provide information, even though it might be needed to take advantage of such IMDb features as My Movies and local show times. </ul></li>|||<ul><li> You can add or update certain information, such as your e-mail address, by using our User Administration pages. When you update information, we usually keep a copy of the prior version for our records. </ul></li>|||<ul><li> If you do not want to receive e-mail or other mail from us, please use our User Administration pages to adjust your preferences. (If you do not want to receive legal notices from us, such as this Privacy Notice, those notices will still govern your use of IMDb, and it is your responsibility to review them for changes.) </ul></li>|||<ul><li> If you do not want us to use personal information that we gather to allow third parties to personalize advertisements we display to you, please adjust your Advertising Preferences. </ul></li>|||<ul><li> The \"help\" portion of the toolbar on most browsers will tell you how to prevent your browser from accepting new cookies, how to have the browser notify you when you receive a new cookie, or how to disable cookies altogether. Additionally, you can disable or delete similar data used by browser add-ons, such as Flash cookies, by changing the add-on's settings or visiting the Web site of its manufacturer. However, because cookies allow you to take advantage of some of IMDb's essential features, we recommend that you leave them turned on. </ul></li>|||<strong> Children </strong><br><br> IMDb is not intended for use by children under the age of 13. If you are under 13, you may not submit information about yourself to IMDb. <br><br>|||<strong> Does IMDb.com Participate in the Safe Harbor Program- </strong><br><br> As a subsidiary of Amazon.com, Inc., IMDb.com is a participant in the Safe Harbor program developed by the U.S. Department of Commerce and (1) the European Union and (2) Switzerland, respectively. Amazon has certified that we adhere to the Safe Harbor Privacy Principles agreed upon by the U.S. and (1) the European Union and (2) Switzerland, respectively. For more information about the Safe Harbor and to view our certification, visit the U.S. Department of Commerce's Safe Harbor Web site. <br><br>|||In compliance with the US-EU and US-Swiss Safe Harbor Principles, we endeavor to resolve all complaints about privacy and the collection or use of customer information. If you have questions about our participation in the Safe Harbor program or have a complaint, please send an e-mail to safeharbor@amazon.com. <br><br>|||Under the Safe Harbor program, any unresolved privacy complaints can be referred to an independent dispute resolution mechanism. We use the BBB EU Safe Harbor Program, which is operated by the Council of Better Business Bureaus. If you feel that we have not satisfactorily addressed your complaint, you can visit the BBB EU Safe Harbor Program web site at www.bbb.org/us/safe-harbor-complaints for more information on how to file a complaint. <br><br>|||<strong> Conditions of Use, Notices, and Revisions </strong><br><br> If you choose to visit IMDb, your visit and any dispute over privacy is subject to this Notice and our Terms and Conditions of Use, including limitations on damages, resolution of disputes, and application of the law of the state of Washington. <br><br>|||If you have any concern about privacy at IMDb, please send us a thorough description to our help desk, and we will try to resolve it. <br><br>|||Our business changes constantly. This Notice and the Terms and Conditions of Use will change also, and use of information that we gather now is subject to the Privacy Notice in effect at the time of use. We may e-mail periodic reminders of our notices and conditions, unless you have instructed us not to, but you should check our Web site frequently to see recent changes. Unless stated otherwise, our current Privacy Notice applies to all information that we have about you and your account. We stand behind the promises we make, however, and will never materially change our policies and practices to make them less protective of customer information collected in the past without the consent of affected customers."
#      ).save()


@app.route('/')
def index():
    # String-based templates
    return render_template_string("""
        {% extends "base.html" %}
	    <h1>{% block title %} Welcome to TILTer {% endblock %}</h1>
        {% block content %}
            <h2>Home page</h2>
            <p><a href={{ url_for('user.register') }}>Register</a></p>
            <p><a href={{ url_for('user.login') }}>Sign in</a></p>
            <p><a href={{ url_for('index') }}>Home page</a> (accessible to anyone)</p>
            <p><a href={{ url_for('member_page') }}>Member page</a> (login required)</p>
            <p><a href={{ url_for('user.logout') }}>Sign out</a></p>
        {% endblock %}
        """)


# User Page by Flask-User
@app.route('/members')
@login_required  # User must be authenticated
def member_page():
    # String-based templates
    return render_template_string("""
        {% extends "base.html" %}
	    <h1>{% block title %} Welcome to TILTer {% endblock %}</h1>
        {% block content %}
            <h2>Members page</h2>
            <p><a href={{ url_for('user.register') }}>Register</a></p>
            <p><a href={{ url_for('user.login') }}>Sign in</a></p>
            <p><a href={{ url_for('index') }}>Home page</a> (accessible to anyone)</p>
            <p><a href={{ url_for('member_page') }}>Member page</a> (login required)</p>
            <p><a href={{ url_for('user.logout') }}>Sign out</a></p>
            <h3><a href={{ url_for('tasks') }}>Tasks</a></h3>
        {% endblock %}
        """)


@app.route('/tasks')
@login_required
def tasks():
    query = Task.objects.all()
    return render_template('tasks.html', tasks=query)


@app.route('/tasks/<string:task_id>')
@login_required
def label(task_id):
    query = Task.objects.get(pk=task_id)
    return render_template('label.html', task=query)
