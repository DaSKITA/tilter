from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, InputRequired


# custom TagListField object, credit: https://gist.github.com/M0r13n/71655c53b2fbf41dc1db8412978bcbf9
class TagListField(StringField):
    """Stringfield for a list of separated tags"""

    def __init__(self, label='', validators=None, separator=' ', **kwargs):
        """
        Construct a new field.
        :param label: The label of the field.
        :param validators: A sequence of validators to call when validate is called.
        :param separator: The separator that splits the individual tags.
        """
        super(TagListField, self).__init__(label, validators, **kwargs)
        self.separator = separator
        self.data = []

    def _value(self):
        if self.data:
            return u', '.join(self.data)
        else:
            return u''

    def process_formdata(self, value_list):
        if value_list:
            self.data = [x.strip() for x in value_list[0].split(self.separator)]


class CreateTaskForm(FlaskForm):
    name = StringField('Name of the Task', validators=[DataRequired()])
    text = TextAreaField('Text', validators=[DataRequired()])
    labels = TagListField('Labels', validators=[InputRequired()], separator=', ')
    html = BooleanField('HTML')
    submit = SubmitField('Create Task')

