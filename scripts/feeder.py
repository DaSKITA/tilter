import json
import os
import requests
import click
from tqdm import tqdm
from pathlib import Path


@click.group()
def cli():
    pass


@click.command()
@click.option('-d', '--directory', default=None, help="Directory which contain Policies as .txt format.")
@click.option('-l', '--language', default="de", help="Language of the policies.")
@click.option('-u', '--url-mapping-path', default=None, help="Url Mapping frpm file name to url")
def jsonify_policies(directory: str, language: str, url_mapping_path: str):
    """
    Transforms a .txt policy into a json file with inputs for the application.
    An URL mapping can be provided to map a file to a url it is retrieved from. If not provided a default
    value will be set.

    Args:
        directory (str): [description]
        language (str): [description]
        url_mapping_path (str): [description]
    """
    if url_mapping_path:
        with open(url_mapping_path, 'r') as mapping_file:
            url_mapping_dict = json.load(mapping_file)

    if not directory:
        directory = os.path.join(Path(os.path.abspath(__file__)).parent.parent, "data")

    for file_name in tqdm(os.listdir(directory)):
        file_path = os.path.join(directory, file_name)

        if os.path.isfile(file_path) and file_name.endswith('.txt'):
            with open(file_path, 'r') as txt_file:
                policy_text = txt_file.read()

            pure_file_name = file_name.split(".")[0]

            json_dict = {
                "text": policy_text,
                "name": pure_file_name,
                "language": language,
                "url": url_mapping_dict[file_name] if url_mapping_path else "no url"
            }
            json_path = os.path.join(Path(os.path.abspath(__file__)).parent.parent, "data", "json_policies")
            if not os.path.isdir(json_path):
                os.makedirs(json_path)
            json_file_path = os.path.join(json_path, f"{pure_file_name}.json")
            with open(json_file_path, "w") as json_write_file:
                json.dump(json_dict, json_write_file)


@click.command()
@click.option('-d', '--directory', default=None, help="Directory of policies.")
def post_tasks(directory: str = None):
    """
    Writes tasks from a json format into the MongoDB. In order to run, the TILTer needs to be
    setup.

    Args:
        directory (str, optional): [description]. Defaults to None.
    """
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
    }

    if not directory:
        directory = os.path.join(Path(os.path.abspath(__file__)).parent.parent, "data", "json_policies")

    file_count = 0
    for file_name in tqdm(os.listdir(directory)):
        # skip hidden files
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path) and file_name.endswith('.json'):

            with open(file_path, 'r') as json_file:
                json_dict = json.load(json_file)

            data = {"name": json_dict["name"], "text": json_dict["text"], "html": False,
                    "url": json_dict["url"], "language": json_dict["language"]}

            requests.post('http://localhost:5000/api/task/', headers=headers, data=json.dumps(data))
            file_count += 1
    print(f"{file_count} files were added to the database.")


if __name__ == "__main__":
    cli.add_command(post_tasks)
    cli.add_command(jsonify_policies)
    cli()
