from database.models import Task, Annotation
from typing import List


class DataHandler:

    def __init__(self) -> None:
        pass

    @staticmethod
    def get_subtasks(task: 'Task') -> List['Task']:
        """Gets all subtasks of a supplied task.

        Returns:
            [type]: [description]
        """
        task_list = []
        for db_task in Task.objects:
            if db_task.parent == task:
                task_list.append(db_task)
                task_list.extend(DataHandler.get_subtasks(db_task))
        return task_list

    @staticmethod
    def get_root_task(task: 'Task') -> 'Task':
        """Gets the root task of a supplied task.

        Returns:
            [type]: [description]
        """
        task = task.get()
        for db_task in Task.objects:
            if task.parent and task.parent == db_task:
                root_task = DataHandler.get_root_task(db_task)
            if not task.parent:
                return task
            if not root_task.parent:
                return root_task

    @staticmethod
    def get_relevant_tasks(task: 'Task') -> List['Task']:
        """Collects all relevant tasks for creating a tilt document, based on the supplied task.
        The root task of the respective task is collected and then all subtasks of the root tasks are
        collected.

        Returns:
            [type]: [description]
        """
        root_task = DataHandler.get_root_task(task)
        task_list = DataHandler.get_subtasks(root_task)
        task_list.append(root_task)
        return task_list

    @staticmethod
    def get_annotations_from_task(task: 'Task') -> 'Annotation':
        """Retrieve all Annotations from a relevant task.

        Returns:
            [type]: [description]
        """
        annotation_list = []
        for annotation_db in Annotation.objects:
            if task == annotation_db.task:
                annotation_list.append(annotation_db)
        return annotation_list

    @staticmethod
    def get_relevant_annotations(task_list: List['Task']) -> List['Annotation']:
        annotation_list = []
        for task in task_list:
            annotation_list.extend(DataHandler.get_annotations_from_task(task))
        return annotation_list


if __name__ == "__main__":
    from mongoengine import connect
    from config import Config

    connect(host=Config.MONGODB_SETTINGS["host"])
    name = "Controller - Company Name - giki.earth"
    task = Task.objects(name=name).get()
    tasks = DataHandler.get_relevant_tasks(task)
    annotations = DataHandler.get_relevant_annotations(tasks)
    print(tasks)
