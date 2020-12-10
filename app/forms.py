from flask_wtf import FlaskForm
from wtforms import BooleanField, FieldList, FormField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class LabelForm(FlaskForm):
    label = StringField('Label')

class CreateTaskForm(FlaskForm):
    name = StringField('Name of the Task', validators=[DataRequired()])
    text = TextAreaField('Text', validators=[DataRequired()])
    labels = FieldList(FormField(LabelForm), min_entries=1)
    html = BooleanField('HTML')
    submit = SubmitField('Create Task')

