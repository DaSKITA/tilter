from typing import List


class TaskSchema:

    def __init__(self, task_list: List):
        pass

    @classmethod
    def create_from_task_id(cls, task_id: int):

        return cls()
