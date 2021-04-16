from api.restx import ns
from config import Config
from database.db import db
from database.models import Task, User, Annotation
from flask import Blueprint, flash, Flask, Markup, render_template, redirect, request
from flask_babel import _, Babel, Domain, get_translations
from flask_restx import Api
from flask_user import login_required, UserManager
from forms import CreateTaskForm
from utils.description_finder import DescriptonFinder


# Initialize Flask App
app = Flask(__name__)
app.config.from_object(Config)
# MongoDB Setup
db.init_app(app)

# Babel Setup
domain = Domain()
babel = Babel(app, default_locale='de')


@babel.localeselector
def get_locale():
    # TODO: this line causes a bug with flask user, the bug prevails after changing it back to return 'en'
    # does not happen in a container!
    return request.accept_languages.best_match(app.config['LANGUAGES'])
    # return "en"


# Character Escaping Filters for Templates
@app.template_filter()
def html_escape(text):
    return Markup(text.replace("'", "&#39;").replace('\r\n', '').replace('\n', '').replace('\r', ''))


# Setup Flask-User and specify the User data-model
user_manager = UserManager(app, db, User)


@app.template_filter()
def txt_escape(text):
    return Markup(text.replace('\r', ''))


# Routing
@app.route('/')
def index():
    # String-based templates

    return render_template('index.html')


@app.route('/members')
@login_required
def member_page():
    # String-based templates
    return render_template('member_page.html')


@app.route('/tasks')
@login_required
def tasks():
    query = Task.objects.all()
    return render_template('tasks.html', tasks=query)


@app.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    form = CreateTaskForm()
    if request.method == 'GET':
        return render_template('create_task.html', form=form)
    else:
        if form.validate_on_submit():
            Task(name=form.name.data, labels=form.labels.data, hierarchy=[], parent=None,
                 interfaces=[
                     "panel",
                     "update",
                     "controls",
                     "side-column",
                     "predictions:menu"],
                 text=form.text.data,
                 html=form.html.data
                 ).save()
            flash("Succesfully created Task " + form.name.data)
        else:
            flash("Error in Validation of sent Form, please check")
        return redirect('/tasks/create')


@app.route('/tasks/<string:task_id>')
@login_required
def label(task_id):
    update_success = request.args.get('success', default=None)
    if update_success:
        flash(_("Annotations updated successfully!"), 'success')
    elif update_success == False:
        flash(_("Error updateing Annotations!"), 'error')

    task = Task.objects.get(pk=task_id)
    annotations = Annotation.objects(task=task)

    description_finder = DescriptonFinder()
    descriptions = description_finder.find_descriptions(task)

    # translate labels
    if get_locale() != "en":
        cache = get_translations()
        labels = [cache._catalog[label] for label in task.labels]
        task.labels = labels

    target_url = request.url_root + 'api/task/' + str(task_id) + '/annotation/json'
    redirect_url = request.base_url
    colors = ['blue', 'red', 'yellow', 'green', 'orange', 'magenta', 'pink']
    return render_template('label.html', task=task, target_url=target_url, annotations=annotations,
                           redirect_url=redirect_url, colors=colors, descriptions=descriptions)


# API Setup
api_bp = Blueprint("api", __name__, url_prefix="/api/")
api = Api(api_bp, version='1.0', title='TILTer API', doc='/docs/',
          description='A simple API granting access to Task & Annotation objects and TILT document conversions')
api.add_namespace(ns)
app.register_blueprint(api_bp)
