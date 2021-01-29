from api.restx import ns
from config import Config
from database.db import db
from database.models import Task, User, Annotation
from flask import flash, Flask, Markup, render_template, redirect, request
from flask_restx import Api
from flask_user import login_required, UserManager
from forms import CreateTaskForm

# Initialize Flask App
app = Flask(__name__)
app.config.from_object(Config)

# MongoDB Setup
db.init_app(app)

# Setup Flask-User and specify the User data-model
user_manager = UserManager(app, db, User)


# Character Escaping Filters for Templates
@app.template_filter()
def html_escape(text):
    return Markup(text.replace("'", "&#39;").replace('\r\n', '').replace('\n', '').replace('\r', ''))


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
            Task(name=form.name.data, labels=form.labels.data,
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
    query = Task.objects.get(pk=task_id)
    target_url = request.url_root + 'api/task/' + str(task_id) + '/annotation/json'
    return render_template('label.html', task=query, target_url=target_url)


# API Setup
api = Api(version='1.0', title='TILTer API', doc='/docs/',
          description='A simple API granting access to Task & Annotation objects and TILT document conversions')
api.add_namespace(ns)
api.init_app(app)
