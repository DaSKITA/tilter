from config import Config
from database.models import Task, Annotation
from flask import request
from flask_restx import fields, Namespace, Resource
from mongoengine import DoesNotExist

from utils.schema_tools import construct_first_level_labels
from utils.create_tilt import create_tilt
from utils.label import AnnotationLabel
from utils.translator import Translator
from tilt_resources.annotation_handler import AnnotationHandler
from tilt_resources.task_creator import TaskCreator

import json
import os
import requests
import fastjsonschema

# API Namespace
ns = Namespace("task", description="API Node for TILTer")

# create models for marshalling
label_fields = AnnotationLabel.for_marshalling()
task_with_id = ns.model('Task', {
    'id': fields.String(required=True, description='Unique identifier of the task'),
    'name': fields.String(required=True, description='Name of the task'),
    'text': fields.String(required=True, description='Task text'),
    'html': fields.Boolean(description='HTML formatted task text'),
    'labels': fields.List(description='Task labels', cls_or_instance=fields.Nested(label_fields)),
    'manual_labels': fields.List(description='Manual Boolean Task labels',
                                 cls_or_instance=fields.Nested(label_fields)),
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
        url = request.json.get('url')
        language = request.json.get("language")

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
                            html=html, text=text)
                task.save()
                meta = Meta(name=name, url=url, root_task=task, language=language)
                meta.save()
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
        task_creator = TaskCreator(task)
        data = request.json
        manual_bools = data.pop('manual_bools', None)
        annotation_handler = AnnotationHandler()
        if manual_bools:
            annotation_handler.create_manual_annotations(manual_bools, task)
        shaped_data = [{
            "task": task,
            "label": translator.translate_reverse(content['results'][0]['value']['labels'][0]),
            "start": content['start'],
            "end": content['end'],
            "text": content['text']} for content in data.values()]
        new_annotations, current_annotations = annotation_handler.filter_new_annotations(shaped_data)
        annotation_handler.synch_task_annotations(task, current_annotations)
        task_creator.create_subtasks(new_annotations)



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


@ns.route('/<string:id>/tilt/publish')
@ns.param('id', 'unique task identifier')
class PushTiltToHub(Resource):
    def post(self, id):
        """
        Pushes the respective tilt-document to the tilt-hub database
        """
        document = create_tilt(id)

        with open('tilt_resources/tilt-complete-schema.json', 'r') as json_file:
            schema = json.load(json_file)
            validate_func = fastjsonschema.compile(schema)
            try:
                validate_func(document)
                validation = 'Validation successful!', True
            except fastjsonschema.exceptions.JsonSchemaValueException as js:
                validation = str(js), False

        response = requests.post(
                   url=os.getenv('TILT_HUB_REST_URL') + '/tilt/tilt',
                   data=json.dumps(document),
                   auth=(os.getenv('TILT_HUB_BASIC_AUTH_USER'), os.getenv('TILT_HUB_BASIC_AUTH_PASSWORD'))
        )

        result = {
            'url' : response.headers.get('location'),
            'validation_successful' : validation[1],
            'validation' : validation[0]
            }

        return result, response.status_code