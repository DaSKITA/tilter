from abc import ABC, abstractmethod
from database.models import Task


class MigrationTask(ABC):

    @abstractmethod
    def run_migration():
        pass


class HtmlTaskTag(MigrationTask):

    def run_migration():
        for task in Task.objects:
            task.update(html=True)


class SubtaskAnnotation(MigrationTask):

    def run_migration():
        # get annotation

        # locate annotation in tilt schema
            # get task
            # get hierarchy
            # locate

        #  verify that it is a child annotation

        # find the parent annotation

        # fill fields

        pass
