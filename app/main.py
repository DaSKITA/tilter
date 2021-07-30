from mongoengine.errors import DoesNotExist
from api.restx import ns

from config import Config

from database.db import db
from database.models import Task, User, Annotation

from flask import Blueprint, flash, Flask, Markup, render_template, redirect, request, url_for
from flask_babel import _, Babel, Domain
from flask_jwt_extended import create_access_token, JWTManager
from flask_restx import Api, fields, Resource
from flask_user import current_user, login_required, UserManager

from utils.schema_tools import get_manual_bools, reduce_schema, retrieve_schema_level
from utils.description_finder import DescriptonFinder
from utils.translator import Translator
from utils.feeder import Feeder

# Initialize Flask App
app = Flask(__name__)
app.config.from_object(Config)
# MongoDB Setup
db.init_app(app)

# Babel Setup
domain = Domain()
babel = Babel(app, default_locale='de')

# Policies
feeder = Feeder(policy_data_dir=Config.POLICY_DIR)
feeder.feed_app_with_policies()


@babel.localeselector
def get_locale():
    # TODO: this line causes a bug with flask user, the bug prevails after changing it back to return 'en'
    # does not happen in a container!
    # return request.accept_languages.best_match(app.config['LANGUAGES'])
    return "en"


# .../tasks/ render helper function
def task_tree_to_dict(task_list):
    task_tree_dict = {}
    for task in task_list:
        task_tree_dict[task] = task_tree_to_dict(Task.objects(parent=task))
    return task_tree_dict

# .../task/__id__/next helper function
def select_next_task(task, previous_seen_task_id, hierarchy=None):
    child_tasks = Task.objects(parent=task)

    if child_tasks:
        if hierarchy:
            # retrieve and reduce local_schema to schema entries that are hierarchically after hierarchy[-1]
            local_schema = retrieve_schema_level(hierarchy[:-1])
            local_schema = reduce_schema(local_schema, hierarchy[-1])

            for entry in local_schema.keys():
                target_hierarchy = hierarchy[:-1] + [entry]
                target_tasks = child_tasks(hierarchy=target_hierarchy).order_by('id')
                if Task.objects.get(id=previous_seen_task_id) in target_tasks:
                    get_next = False
                    for task in target_tasks:
                        if get_next:
                            return task.id
                        elif task.id == previous_seen_task_id:
                            get_next = True
                elif target_tasks:
                    return target_tasks.first().id
        else:
            # no hierarchy given (first iteration)
            # return the first child according to schema
            local_schema = retrieve_schema_level(task.hierarchy)

            for entry in local_schema.keys():
                target_hierarchy = task.hierarchy + [entry] if task.hierarchy else [entry]
                target_tasks = child_tasks(hierarchy=target_hierarchy).order_by('id')
                if target_tasks:
                    return target_tasks.first().id

    return None


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


@app.route('/tasks/<string:task_id>/next')
@login_required
def redirect_to_next_task(task_id, previous_seen_task_id=None, hierarchy=None):
    try:
        task = Task.objects.get(id=task_id)
        # select first child task according to schema
        next_task = select_next_task(task, previous_seen_task_id=previous_seen_task_id, hierarchy=hierarchy)
        if next_task:
            return redirect(url_for("label", task_id=next_task))
        else:
            if task.parent:
                # there may be siblings
                return redirect_to_next_task(task_id=task.parent.id, previous_seen_task_id=task.id,
                                            hierarchy=task.hierarchy)
            else:
                # there are no siblings left, therefore the annotation process is finished
                flash(_("Finished annotating all subtasks!"), 'success')
                return redirect(url_for("tasks"))
    except DoesNotExist:
        return redirect(url_for("tasks"))


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
    try:
        task = Task.objects.get(pk=task_id)
        annotations = Annotation.objects(task=task)
    except DoesNotExist:
        return redirect(url_for('tasks'))

    # finds the descriptions for labels and manual bools of this task
    description_finder = DescriptonFinder()
    annotation_descriptions = description_finder.find_descriptions(task.labels, task.hierarchy)
    annotation_descriptions = annotation_descriptions.get_descriptions()
    tooltips = description_finder.find_descriptions(task.manual_labels, task.hierarchy)
    tooltips = tooltips.get_descriptions()

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

    # handle manual bool annotation alert
    if manual_bools:
        flash("To complete this task hit use on of the Update buttons and fill out the remaining fields!", 'info')

    token = create_access_token(identity=current_user.username)

    return render_template('label.html', task=task, target_url=target_url, annotations=annotations,
                           redirect_url=redirect_url, colors=colors,
                           annotation_descriptions=annotation_descriptions,
                           manual_bools=manual_bools, tooltips=tooltips, token=token)


# API Setup
api_bp = Blueprint("api", __name__, url_prefix="/api/")
api = Api(api_bp, version='1.0', title='TILTer API', doc='/docs/',
          description='A simple API granting access to Task & Annotation objects and TILT document conversions')
api.add_namespace(ns)
app.register_blueprint(api_bp)

jwt = JWTManager(app)

user = api.model('User', {
    'username': fields.String(required=True, description="Username"),
    'password': fields.String(required=True, description="Password")
})


@api.route("/auth")
class Authentication(Resource):

    @api.expect(user)
    def post(self):
        username = request.json.get("username", None)
        password = request.json.get("password", None)

        try:
            current_user = User.objects.get(username=username)
        except Exception:
            return {"msg": "Wrong username or password"}, 401

        if user_manager.password_manager.verify_password(password=password,
                                                         password_hash=current_user.password):
            access_token = create_access_token(identity=username)
            return access_token, 200
        else:
            return {"msg": "Wrong username or password"}, 401


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", use_debugger=False, use_reloader=False, passthrough_errors=True)
