import json
import os
from tqdm import tqdm
from config import Config
from tilt_resources.task_creator import TaskCreator


class Feeder:

    def __init__(self, policy_data_dir: str) -> None:
        if policy_data_dir:
            self.policy_data_dir = policy_data_dir
        else:
            print("Choosing default data directory under: <prj-path>/data/official_policies")
            self.policy_data_dir = os.path.join(Config.ROOT_PATH, "data/official_policies")
        self.task_creator = TaskCreator()

    def feed_app_with_policies(self):
        file_count = 0
        json_file_names = [file_name
                           for file_name in os.listdir(self.policy_data_dir) if file_name.endswith(".json")]
        for file_name in tqdm(json_file_names):
            # skip hidden files
            file_path = os.path.join(self.policy_data_dir, file_name)
            if os.path.isfile(file_path):
                with open(file_path, 'r') as json_file:
                    json_dict = json.load(json_file)
                self.task_creator.create_root_task(name=json_dict["name"],
                                                   text=json_dict["text"],
                                                   url=json_dict["url"])
                file_count += 1
        print(f"{file_count} files were added to the database.")
