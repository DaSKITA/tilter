from api.restx import ns
from config import Config
from database.db import db
from database.models import Task, User, Annotation
from flask import Blueprint, flash, Flask, Markup, render_template, redirect, request, url_for
from flask_babel import _, Babel, Domain
from flask_restx import Api
from flask_user import current_user, login_required, UserManager
from forms import CreateTaskForm
from utils.schema_tools import get_manual_bools, construct_first_level_labels
from utils.description_finder import DescriptonFinder, ManualBoolDescriptonFinder
from utils.translator import Translator

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
    # return request.accept_languages.best_match(app.config['LANGUAGES'])
    return "en"


# .../tasks/ render helper function
def task_tree_to_dict(tasks):
    task_tree_dict = {}
    for task in tasks:
        task_tree_dict[task] = task_tree_to_dict(Task.objects(parent=task))
    return task_tree_dict


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
    if current_user.is_authenticated:
        return redirect(url_for('tasks'))
    else:
        return render_template('index.html')


@app.route('/tasks')
@login_required
def tasks():
    # tasks = gather_task_list()
    tasks = task_tree_to_dict(Task.objects(parent=None))
    return render_template('tasks.html', tasks=tasks)


@app.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    form = CreateTaskForm()
    if request.method == 'GET':
        return render_template('create_task.html', form=form)
    else:
        if form.validate_on_submit():
            labels = construct_first_level_labels()
            Task(name=form.name.data, labels=labels, hierarchy=[], parent=None,
                 interfaces=[
                     "panel",
                     "update",
                     "controls",
                     "side-column",
                     "predictions:menu"],
                 text=form.text.data,
                 html=form.html.data
                 ).save()
            flash("Succesfully created Task " + form.name.data, 'success')
        else:
            flash("Error in Validation of sent Form, please check", 'error')
        return redirect('/tasks/create')


@app.route('/tasks/<string:task_id>')
@login_required
def label(task_id):
    # handle success message, after clicking update button
    update_success = request.args.get('success', default=None)
    if update_success == "true":
        flash(_("Annotations updated successfully!"), 'success')
    elif update_success == "false":
        flash(_("Error updateing Annotations!"), 'error')

    # get task and its annotations
    task = Task.objects.get(pk=task_id)
    annotations = Annotation.objects(task=task)

    # finds the descriptions for labels of this task
    description_finder = DescriptonFinder()
    descriptions = description_finder.find_descriptions(task)

    # finds the descriptions for manual bools of this task
    # manual_bools_description_finder = ManualBoolDescriptonFinder()
    # tooltips = manual_bools_description_finder.find_manual_bool_descriptions(task)
    # TODO
    tooltips = ["Tooltip test for legalRequirement",
                "Tooltip test for contractualRegulation",
                "Tooltip test for obligationToProvide"]

    # translate labels
    translator = Translator()
    [label.update(name=translator.translate(label["name"])) for label in task.labels]

    # define the API target url and the url to redirect to
    target_url = request.url_root + 'api/task/' + str(task_id) + '/annotation/json'
    redirect_url = request.base_url

    # define colors for labels
    colors = ['blue', 'red', '#1CBA3D', '#13812A', 'orange', 'magenta', 'pink', 'brown', '#B986D4', '#8FA1E2', 'dimgrey',
              '#0A4216', 'darksalmon']

    # decide if postprocessing is needed before sending LSF completion to API url
    manual_bools = get_manual_bools(task.hierarchy)

    return render_template('label.html', task=task, target_url=target_url, annotations=annotations,
                           redirect_url=redirect_url, colors=colors, descriptions=descriptions,
                           manual_bools=manual_bools, tooltips=tooltips)


# API Setup
api_bp = Blueprint("api", __name__, url_prefix="/api/")
api = Api(api_bp, version='1.0', title='TILTer API', doc='/docs/',
          description='A simple API granting access to Task & Annotation objects and TILT document conversions')
api.add_namespace(ns)
app.register_blueprint(api_bp)

if __name__ == "__main__":
    app.run(use_debugger=False, use_reloader=False, passthrough_errors=True)
