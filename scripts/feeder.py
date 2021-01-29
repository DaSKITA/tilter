from pathlib import Path

import codecs
import json
import os
import requests
import sys

def main(argv):
    headers = {
    'Content-Type': 'application/json; charset=utf-8',
    }

    if len(argv) != 1:
        print("Usage: python feeder.py [directory of policies]")
        return

    directory = argv[0]

    for file in os.listdir(directory):

        textfile = open(directory + "/" + file, "r", encoding="utf-8")
        print(directory + "/" + file)
        text = textfile.read()
        textfile.close()

        data = {"name": file[:-4], "text": text, "html": False,
                "labels": ["Controller - Name", "Data Protection Officer - Email", "Third Country Transfer - Target Country"]}

        response = requests.post('http://localhost:5000/api/task', headers=headers, data=json.dumps(data))

        print(response.status_code)
        print(response.text)

if __name__ == "__main__":
    main(sys.argv[1:])
