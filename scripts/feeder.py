
import json
import os
import requests
import click
from tqdm import tqdm


@click.command()
@click.option('-d', '--directory', default=None, help="Directory of policies.")
def main(directory: str):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
    }

    assert directory, "No Input Files provided!"

    for file in tqdm(os.listdir(directory)):
        # skip hidden files
        if file.startswith('.'):
            continue

        textfile = open(directory + "/" + file, "r")
        text = textfile.read()
        textfile.close()

        data = {"name": file[:-4], "text": text, "html": False}

        response = requests.post('http://localhost:5000/api/task/', headers=headers, data=json.dumps(data))


if __name__ == "__main__":
    main()
