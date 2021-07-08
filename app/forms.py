from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class CreateTaskForm(FlaskForm):
    name = StringField('Name of the Task', validators=[DataRequired()])
    text = TextAreaField('Text', validators=[DataRequired()])
    html = BooleanField('HTML')
    submit = SubmitField('Create Task')

