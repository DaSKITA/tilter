import json
import os
import requests
import click
from tqdm import tqdm
from pathlib import Path


@click.command()
@click.option('-d', '--directory', default=None, help="Directory of policies.")
def main(directory: str = None):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
    }

    if not directory:
        directory = os.path.join(Path(os.path.abspath(__file__)).parent.parent, "data")

    file_count = 0
    for file_name in tqdm(os.listdir(directory)):
        # skip hidden files
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path) and file_name.endswith('.txt'):

            textfile = open(file_path, "r")
            text = textfile.read()
            textfile.close()

            data = {"name": file_name[:-4], "text": text, "html": False}

            _ = requests.post('http://localhost:5000/api/task/', headers=headers, data=json.dumps(data))
            file_count += 1
    print(f"{file_count} files were added to the database.")


if __name__ == "__main__":
    main()
