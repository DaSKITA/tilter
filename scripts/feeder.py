import json
import os
import requests
import click
from tqdm import tqdm
from pathlib import Path
from langdetect import detect


@click.group()
def cli():
    pass


@click.command()
@click.option('-d', '--directory', default=None, help="Directory which contain Policies as .txt format.")
@click.option('-u', '--url-mapping-path', default=None, help="Url Mapping from file name to url")
@click.option('-o', '--output_path', default=None, help="Output path - the path where the jsonified policies \
    go.")
def jsonify_policies(directory: str, url_mapping_path: str, output_path: str):
    """
    Transforms a .txt policy into a json file with inputs for the application.
    An URL mapping can be provided to map a file to a url it is retrieved from. If not provided a default
    value will be set.

    Args:
        directory (str): [description]
        language (str): [description]
        url_mapping_path (str): [description]
    """
    # TODO: language identification with langid or similar libs
    print("Forming Jsons...")
    if url_mapping_path:
        with open(url_mapping_path, 'r') as mapping_file:
            url_mapping_dict = json.load(mapping_file)
    else:
        url_mapping_dict = {}

    if not directory:
        directory = os.path.join(Path(os.path.abspath(__file__)).parent.parent, "data")

    for file_name in tqdm(os.listdir(directory)):
        file_path = os.path.join(directory, file_name)

        if os.path.isfile(file_path) and file_name.endswith('.txt'):
            with open(file_path, 'r') as txt_file:
                policy_text = txt_file.read()
            language = detect(policy_text)
            url = url_mapping_dict.get(file_name)
            pure_file_name = file_name.split(".")[0]

            json_dict = {
                "text": policy_text,
                "name": pure_file_name,
                "language": language,
                "url": url if url else "no url"
            }

            if not output_path:
                output_path = os.path.join(Path(os.path.abspath(__file__)).parent.parent, "data",
                                           "json_policies")
            if not os.path.isdir(output_path):
                os.makedirs(output_path)
            json_file_path = os.path.join(output_path, f"{pure_file_name}.json")
            with open(json_file_path, "w") as json_write_file:
                json.dump(json_dict, json_write_file)


@click.command()
@click.option('-d', '--directory', default=None, help="Directory of policies.")
@click.option('-u', '--url', default=None, help="Url of the host to send to")
@click.option('-n', '--username', default=None, help="Username for Authentication")
@click.option('-p', '--password', default=None, help="Password for Authentication")
def post_tasks(directory: str = None, url: str = None, username: str = None, password: str = None):
    """
    Writes tasks from a json format into the MongoDB. In order to run, the TILTer needs to be
    setup.

    Args:
        directory (str, optional): [description]. Defaults to None.
    """
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
    }
    # print("Fetching API Auth Token.")
    # data = {
    #     "username": username,
    #     "password": password,
    # }
    # token = requests.post(f'{url}/api/auth/', headers=headers, data=json.dumps(data)).json()
    # headers['Authorization'] = token
    print("Sending policies to database.")
    if not url:
        url = "http://localhost:5000"
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

            requests.post(f'{url}/api/task/', headers=headers, data=json.dumps(data))
            file_count += 1
    print(f"{file_count} files were added to the database.")


if __name__ == "__main__":
    cli.add_command(post_tasks)
    cli.add_command(jsonify_policies)
    cli()
