import json

def put_cache(prompt, response, file_path="cache.json", is_json=True):
    if not is_json:
        response = {'result': response}

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    data[prompt] = response

    with open(file_path, 'w') as file:
        json.dump(data, file)

def get_cache(prompt, file_path="cache.json", is_json=True):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    if prompt in data:
        result = data[prompt]
        
        if not is_json:
            result = result['result']

        return result
    else:
        return None
