from database.models import Task, Annotation
from flask import request
from flask_restx import fields, Namespace, Resource

# API Namespace
ns = Namespace("api", description="API Node for TILTer")

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


# TODO: CORRECT RESPONSES
@ns.route('/task')
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
        name = request.json.get('name')
        text = request.json.get('text')
        html = request.json.get('html')
        labels = request.json.get('labels')
        if name != '' and text != '' and labels != '':
            new_task = Task(name=name, labels=labels,
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


@ns.route('/task/<string:id>')
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


@ns.route('/task/<string:id>/annotation')
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


@ns.route('/task/<string:id>/annotation/json')
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
            return resp, 200
        else:
            return [], 400


@ns.route('/task/tilt')
class TiltDocumentCollection(Resource):

    def get(self):
        """
        Fetches the tilt representation of a all tasks with their current annotations in JSON
        :return: JSON tilt representation of all tasks
        """
        # create json and fill it
        for task in Task.objects:
            for anno in Annotation.objects(task=task):
                anno
        return None, 200


@ns.route('/task/<string:id>/tilt')
@ns.param('id', 'unique task identifier')
class TiltDocumentByTaskId(Resource):

    def get(self, id):
        """
        Fetches the tilt representation of the task with given id with their current annotations in JSON
        :param id: unique id of the task
        :return: JSON tilt representation of all tasks
        """
        # create json and fill it
        for anno in Annotation.objects(task=Task.objects(id=id)):
            anno
        return None, 200
