import json


def load_json(path: str):
    # Read json file
    with open(path, 'r') as auth_file:
        data = auth_file.read()

    # Convert to a json object
    return json.loads(data)
