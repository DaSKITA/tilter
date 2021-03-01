from database.models import Annotation


def tilt_from_task(task):
    annotations = Annotation(task=task)
    return annotations
