from config import Config
from database.models import Task, Annotation
from flask import request
from flask_restx import fields, Namespace, Resource
from mongoengine import DoesNotExist
from utils.schema_tools import construct_first_level_labels, new_subtask_needed
from utils.create_tilt import create_tilt
from utils.label import Label
from utils.translator import Translator

# API Namespace
ns = Namespace("task", description="API Node for TILTer")

# create models for marshalling
label_fields = Label.for_marshalling()
task_with_id = ns.model('Task', {
    'id': fields.String(required=True, description='Unique identifier of the task'),
    'name': fields.String(required=True, description='Name of the task'),
    'text': fields.String(required=True, description='Task text'),
    'html': fields.Boolean(description='HTML formatted task text'),
    'labels': fields.List(description='Task labels', cls_or_instance=fields.Nested(label_fields)),
})

task_no_id_or_label = ns.model('Task', {
    'name': fields.String(required=True, description='Name of the task'),
    'text': fields.String(required=True, description='Task text'),
    'html': fields.Boolean(description='HTML formatted task text'),
})

annotation = ns.model('Annotation', {
    'text': fields.String(description='Annotation text'),
    'label': fields.String(description='Annotation label'),
    'start': fields.Integer(description='Starting Position of Annotation'),
    'end': fields.Integer(description='Ending Position of Annotation'),
})


@ns.route('/')
class TaskCollection(Resource):

    @ns.marshal_with(task_with_id, as_list=True)
    def get(self):
        """
        :return: list of tasks.
        """
        return list(Task.objects)

    @ns.expect(task_no_id_or_label)
    @ns.marshal_with(task_with_id)
    def post(self):
        """
        Creates a new task and returns it.
        :return: newly created task
        """
        schema = Config.SCHEMA_DICT
        labels = construct_first_level_labels(as_dict=True)

        name = request.json.get('name')
        text = request.json.get('text')
        html = request.json.get('html')
        if name != '' and text != '':
            try:
                task = Task.objects.get(name=name, labels=labels, hierarchy=[], parent=None, html=html,
                                        text=text)
            except DoesNotExist:
                task = Task(name=name, labels=labels, hierarchy=[], parent=None,
                            interfaces=[
                            "panel",
                            "update",
                            "controls",
                            "side-column",
                            "predictions:menu"],
                            html=html, text=text,
                            desc_keys=schema.keys())
                task.save()
                return task, 201
            else:
                return task, 200
        else:
            return None, 400


@ns.route('/<string:id>')
@ns.param('id', 'unique task identifier')
class TaskById(Resource):

    @ns.marshal_with(task_with_id)
    def get(self, id):
        """
        Fetches task by the given id and returns it.
        :param id: unique id of the task
        :return: task with given id
        """
        return Task.objects.get(id=id)

    def delete(self, id):
        """
        Deletes task with given id
        :param id: unique id of the task
        :return: TODO
        """
        return Task.objects.get(id=id).delete()


@ns.route('/<string:id>/annotation')
@ns.param('id', 'unique task identifier')
class AnnotationByTaskId(Resource):

    @ns.marshal_with(annotation, as_list=True)
    def get(self, id):
        """
        Fetches annotations by the id of a task and returns it.
        :param id: unique id of the task
        :return: annotations of task with given id
        """
        task = Task.objects(id=id)
        return list(Annotation.objects(task=task))

    @ns.expect(annotation)
    @ns.marshal_with(annotation)
    def post(self, id):
        """
        Creates a new annotation for task with given id and returns it.
        :param id: unique id of the task
        :return: newly created annotation
        """
        task = Task.objects.get(id=id)
        text = request.json.get('text')
        label = request.json.get('label')
        start = request.json.get('start')
        end = request.json.get('end')
        if text != '' and label != '' and start and end:
            new_annotation = Annotation(task=task, label=label, text=text, start=start, end=end)
            new_annotation.save()
            return new_annotation
        else:
            return None, 400


@ns.route('/<string:id>/annotation/json')
@ns.param('id', 'unique task identifier')
class AnnotationByTaskIdInJSON(Resource):

    @ns.marshal_with(annotation, as_list=True)
    def post(self, id):
        """
        Creates new annotations for a task with given id and returns them.
        Also creates new subtasks according to schema.json, if there have been
        annotations made, which open a new hierarchical level.
        :param id: unique id of the task
        :return: newly created annotation
        """
        translator = Translator()
        # get the task and posted annotations
        task = Task.objects.get(id=id)
        data = request.json
        all_current_annotations = []
        new_annotations = []

        # prepare reverse translations, if the client is using another language but english

        # iterate through all posted annotations and create new annotation objects
        for content in data.values():
            # get the label and translate it back if necessary
            label = content['results'][0]['value']['labels'][0]
            label = translator.translate_reverse(label)
            start = content['start']
            end = content['end']
            text = content['text']
            # try to find an already existing annotation with the same content
            try:
                old_annotation = Annotation.objects.get(task=task, text=text, start=start, end=end, label=label)
                all_current_annotations.append(old_annotation.id)
            # if there is no old annotation, create a new one
            except DoesNotExist:
                new_annotation = Annotation(task=task, text=text, start=start, end=end, label=label)
                new_annotation.save()
                new_annotations.append(new_annotation)
                all_current_annotations.append(new_annotation.id)

        # delete old annotations, that did not appear in the POST data
        for anno in Annotation.objects(task=task):
            if anno.id not in all_current_annotations:
                anno.delete()

        # create new tasks according to the tilt schema
        # load tilt schema file
        schema = Config.SCHEMA_DICT

        # advance in tilt schema until reaching the hierarchy level of the current task
        for j in task.hierarchy:
            try:
                schema = schema[j]
            except:
                schema = schema[0][j]

        # if schema is now a list, we need to get the dict inside of it
        if type(schema) is list:
            schema = schema[0]

        # iterate through newly created annotations and create a new task, if necessary
        for anno in new_annotations:
            # look through all entries in the current hierarchy level of the schema
            for i in schema.keys():
                entry = schema[i]

                # if the entry is a list we need to look inside the list instead
                if type(entry) is list:
                    entry = entry[0]

                # if the entry is not a dict, the annotation does not open a new hierarchical level
                if type(entry) is not dict:
                    continue

                # since the entry is a dict, check if there is a new subtask to be created
                # a new subtask is needed if the entry holds more than 1 non-artifical value or holds another dict
                if entry['_desc'] == anno.label and new_subtask_needed(entry):
                    # creation of new task is needed, gather labels, create new hierarchy list and determine new name
                    labels = []
                    desc_keys = []
                    for key, val in entry.items():
                        label_limited = True
                        # if the entry is a list, the label can be annotated more than once
                        if type(val) is list:
                            val = val[0]
                            label_limited = False
                        # if the entry is a dict, save a label using the entry's _desc field
                        if type(val) is dict:
                            label = Label(name=val['_desc'], multiple=label_limited)
                            labels.append(label.to_dict())
                            desc_keys.append(key)
                        # if the key is a boolean or an artificial field, skip it
                        elif key[0] in ['_', '~']:
                            continue
                        # the entry is a simple string
                        else:
                            label = Label(name=val, multiple=label_limited)
                            labels.append(label.to_dict())
                            desc_keys.append(key)

                    # copy the hierarchy list and append current hierarchical level
                    hierarchy = task.hierarchy.copy()
                    hierarchy.append(i)

                    # name the new task in accordance to the root task
                    tmp_task = task
                    while tmp_task.parent is not None:
                        tmp_task = tmp_task.parent
                    text = anno.text if len(anno.text) <= 20 else anno.text[:20] + '...'
                    name = anno.label + ' (' + text + ')' + ' - ' + tmp_task.name

                    # create new task
                    new_task = Task(name=name, labels=labels,
                                    hierarchy=hierarchy, parent=task,
                                    interfaces=[
                                        "panel",
                                        "update",
                                        "controls",
                                        "side-column",
                                        "predictions:menu"],
                                    html=task.html,
                                    text=task.text,
                                    desc_keys=desc_keys)
                    new_task.save()

                    new_task_anno_label = entry[entry['_key']] if type(entry[entry['_key']]) is not list else entry[entry['_key']][0]
                    # create annotation for new task
                    new_task_anno = Annotation(task=new_task, label=new_task_anno_label, text=anno.text,
                                               start=anno.start, end=anno.end)
                    new_task_anno.save()
        return new_annotations


@ns.route('/tilt')
class TiltDocumentCollection(Resource):

    def get(self):
        """
        Fetches the tilt representation of a all tasks with their current annotations in JSON
        :return: JSON tilt representation of all tasks
        """
        documents = []
        for task in Task.objects(parent=None):
            documents.append(create_tilt(task.id))
        return documents, 200


@ns.route('/<string:id>/tilt')
@ns.param('id', 'unique task identifier')
class TiltDocumentByTaskId(Resource):

    def get(self, id):
        """
        Fetches the tilt representation of the task with given id with their current annotations in JSON
        :param id: unique id of the task
        :return: JSON tilt representation of all tasks
        """
        return create_tilt(id), 200
