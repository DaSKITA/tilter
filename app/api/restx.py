from database.models import Task, Annotation
from flask import request
from flask_restx import fields, Namespace, Resource
from mongoengine import DoesNotExist
from flask_babel import get_translations, get_locale
from data_handling.data_handler import DataHandler
from tilt_resources.tilt_creator import TiltCreator
from config import Config

import json
import os
import requests
import fastjsonschema

# API Namespace
ns = Namespace("task", description="API Node for TILTer")

# create models for marshalling
task_with_id = ns.model('Task', {
    'id': fields.String(required=True, description='Unique identifier of the task'),
    'name': fields.String(required=True, description='Name of the task'),
    'text': fields.String(required=True, description='Task text'),
    'html': fields.Boolean(description='HTML formatted task text'),
    'labels': fields.List(description='Task labels', cls_or_instance=fields.String),
})

task_no_id = ns.model('Task', {
    'name': fields.String(required=True, description='Name of the task'),
    'text': fields.String(required=True, description='Task text'),
    'html': fields.Boolean(description='HTML formatted task text'),
    'labels': fields.List(description='Task labels', cls_or_instance=fields.String),
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

    @ns.expect(task_no_id)
    @ns.marshal_with(task_with_id)
    def post(self):
        """
        Creates a new task and returns it.
        :return: newly created task
        """
        labels = []

        # open tilt schema file
        cur_path = os.path.dirname(__file__)
        new_path = os.path.join(cur_path, '..', 'tilt_resources', 'schema.json')
        with open(new_path, 'r') as f:
            schema = json.load(f)

        # construct first-level labels from tilt schema
        for i in schema.keys():
            labels.append(schema[i]["desc"])

        name = request.json.get('name')
        text = request.json.get('text')
        html = request.json.get('html')
        if name != '' and text != '':
            try:
                task = Task.objects.get(name=name, labels=labels, hierarchy=[], parent=None, html=html, text=text)
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
        Creates a new annotation for task with given id and returns it.
        :param id: unique id of the task
        :return: newly created annotation
        """
        task = Task.objects.get(id=id)
        data = request.json
        all_current_annotations = []
        new_annotations = []
        translation_dict = None
        if get_locale() != "en":
            cache = get_translations()
            translation_dict = {value: key for key, value in cache._catalog.items()}

        # create new annotations
        for content in data.values():

            label = content['results'][0]['value']['labels'][0]
            if translation_dict:
                label = translation_dict[label]
            start = content['start']
            end = content['end']
            text = content['text']
            try:
                old_annotation = Annotation.objects.get(task=task, text=text, start=start, end=end, label=label)
                all_current_annotations.append(old_annotation.id)
            except DoesNotExist:
                new_annotation = Annotation(task=task, text=text, start=start, end=end, label=label)
                new_annotation.save()
                new_annotations.append(new_annotation)
                all_current_annotations.append(new_annotation.id)

        # delete old unwanted annotations
        for anno in Annotation.objects(task=task):
            if anno.id not in all_current_annotations:
                anno.delete()

        # create new tasks according to the tilt schema
        # open tilt schema file
        cur_path = os.path.dirname(__file__)
        new_path = os.path.join(cur_path, '..', 'tilt_resources', 'schema.json')
        with open(new_path, 'r') as f:
            schema = json.load(f)

        # advance in tilt schema until reaching the hierarchy level of the current task
        for j in task.hierarchy:
            schema = schema[j]

        # iterate through newly created annotations and create a new task, if necessary
        for anno in new_annotations:
            for i in schema.keys():
                if type(schema[i]) is not dict:
                    continue
                if schema[i]['desc'] == anno.label and \
                        (len(schema[i].values()) > 3 or any(isinstance(val, dict) for val in schema[i].values())):
                    # creation of new task is needed, gather labels, create new hierarchy list and determine new name
                    labels = []
                    for key, val in schema[i].items():
                        if type(val) is dict:
                            labels.append(val['desc'])
                        elif key in ['desc', 'key']:
                            continue
                        else:
                            labels.append(val)

                    hierarchy = task.hierarchy.copy()
                    hierarchy.append(i)

                    tmp_task = task
                    while tmp_task.parent is not None:
                        tmp_task = tmp_task.parent
                    name = anno.label + ' - ' + tmp_task.name

                    # create new task
                    new_task = Task(name=name, labels=labels,
                                    hierarchy=hierarchy, parent=task,
                                    interfaces=[
                                        "panel",
                                        "update",
                                        "controls",
                                        "side-column",
                                        "predictions:menu"],
                                    html=task.html, text=task.text)
                    new_task.save()

                    # create annotation for new task
                    new_task_anno = Annotation(task=new_task, label=schema[i][schema[i]['key']], text=anno.text,
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
        tilt_creator = TiltCreator()
        for task in Task.objects:
            relevant_tasks = DataHandler.get_relevant_tasks(task)
            annotations = DataHandler.get_relevant_annotations(relevant_tasks)
            tilt_dict = tilt_creator.create_tilt_document(annotations)
            documents.append(tilt_dict)
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
        tilt_creator = TiltCreator()
        task = Task.objects(id=id).get()
        relevant_tasks = DataHandler.get_relevant_tasks(task)
        annotations = DataHandler.get_relevant_annotations(relevant_tasks)
        tilt_dict = tilt_creator.create_tilt_document(annotations)
        return tilt_dict, 200


@ns.route('/<string:id>/push-to-tilt-hub')
@ns.param('id', 'unique task identifier')
#@ns.param('validation', 'toggle JSON schema validation', type=bool)
class PushTiltToHub(Resource):
    def post(self, id):
        """
        Pushes the respective tilt-document to the tilt-hub database
        """
        # Next 4 lines: Copy-paste from above future legacy get()
        tilt_creator = TiltCreator()
        task = Task.objects(id=id).get()
        relevant_tasks = DataHandler.get_relevant_tasks(task)
        annotations = DataHandler.get_relevant_annotations(relevant_tasks)
        tilt = tilt_creator.create_tilt_document(annotations)

        print(request.form['validation'])


  #       if request.form['validation'] == True: # FIXME
  #          with open('tilt_resources/tilt-complete-schema.json', 'r') as json_file:
  #              schema = json.load(json_file)
  #              validate_func = fastjsonschema.compile(schema)
  #              try:
  #                  validate_func(tilt)
  #              except fastjsonschema.exceptions.JsonSchemaValueException as js:
  #                  validation_errors =  { 
  #                      'error': 'Could not validate document!',
  #                      'details': str(js)
  #                      }
  #                  return validation_errors, 400

        response = requests.post(
                   url=os.getenv('TILT_HUB_REST_URL') + '/tilt/tilt',
                   data=json.dumps(tilt),
                   auth=(os.getenv('TILT_HUB_BASIC_AUTH_USER'), os.getenv('TILT_HUB_BASIC_AUTH_PASSWORD'))
        )
        return response.headers.get('location'), response.status_code