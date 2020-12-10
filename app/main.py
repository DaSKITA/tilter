from config import Config
from flask import flash, Flask, Markup, render_template, redirect, render_template_string, request
from flask_mongoengine import MongoEngine
from flask_user import login_required, UserManager, UserMixin
from forms import CreateTaskForm

# Flask App
app = Flask(__name__)
app.config.from_object(Config)

# MongoDB Setup
db = MongoEngine()
db.init_app(app)

# Character Escaping Filters for Templates
@app.template_filter()
def html_escape(text):
    return Markup(text.replace("'", "&#39;").replace('\r\n', '').replace('\n', '').replace('\r', ''))

@app.template_filter()
def txt_escape(text):
    return Markup(text.replace('\r\n', '<br>').replace('\n', '<br>').replace('\r', '<br>'))

# Model Entries
class Task(db.Document):
    name = db.StringField(max_length=255)
    labels = db.ListField()
    interfaces = db.ListField()
    text = db.StringField()
    html = db.BooleanField()


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


# Routing
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
                     "completions:menu",
                     "completions:add-new",
                     "completions:delete",
                     "predictions:menu"],
                 text=form.text.data,
                 html=form.html.data
                 ).save()
            flash("Succesfully created Task " + form.name.data)
            return redirect('/tasks/create')
        else:
            flash("Error in Validation of sent Form, please check")
            return redirect('/tasks/create')


@app.route('/tasks/<string:task_id>')
@login_required
def label(task_id):
    query = Task.objects.get(pk=task_id)
    return render_template('label.html', task=query)
