from database.models import Task, Annotation
from flask import request
from flask_restx import fields, Namespace, Resource
from tilt.utilities import tilt_from_task

import json
import os

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
        new_path = os.path.join(cur_path, '..', 'tilt', 'schema.json')
        with open(new_path, 'r') as f:
            schema = json.load(f)

        # construct first-level labels from tilt schema
        for i in schema.keys():
            labels.append(schema[i]["desc"])

        name = request.json.get('name')
        text = request.json.get('text')
        html = request.json.get('html')
        if name != '' and text != '':
            new_task = Task(name=name, labels=labels, hierarchy=[], parent=None,
                 interfaces=[
                     "panel",
                     "update",
                     "controls",
                     "side-column",
                     "predictions:menu"],
                 html=html, text=text)
            new_task.save()
            return new_task
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
        return Task.objects(id=id)

    def delete(self, id):
        """
        Deletes task with given id
        :param id: unique id of the task
        :return: TODO
        """
        return Task.objects(id=id).delete()


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
        resp = []
        for content in data.values():
            label = content['results'][0]['value']['labels'][0]
            start = content['start']
            end = content['end']
            text = content['text']
            print(label)
            if not Annotation.objects(task=task, text=text, start=start, end=end, label=label):
                new_annotation = Annotation(task=task, text=text, start=start, end=end, label=label)
                new_annotation.save()
                resp.append(new_annotation)
        if resp:
            return resp
        else:
            return [], 400


@ns.route('/tilt')
class TiltDocumentCollection(Resource):

    def get(self):
        """
        Fetches the tilt representation of a all tasks with their current annotations in JSON
        :return: JSON tilt representation of all tasks
        """
        documents = []
        for task in Task.objects:
            documents.append(tilt_from_task(task))
        return list(documents), 200


@ns.route('/<string:id>/tilt')
@ns.param('id', 'unique task identifier')
class TiltDocumentByTaskId(Resource):

    def get(self, id):
        """
        Fetches the tilt representation of the task with given id with their current annotations in JSON
        :param id: unique id of the task
        :return: JSON tilt representation of all tasks
        """
        task = Task.objects(id=id)
        return tilt_from_task(task), 200
