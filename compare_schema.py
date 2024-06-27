import os
import requests
from bs4 import BeautifulSoup
import json
from deepdiff import DeepDiff
import re

def preprocess_schema(schema):
    if isinstance(schema, dict):
        return {k: preprocess_schema(v) for k, v in schema.items()}
    elif isinstance(schema, list):
        return [preprocess_schema(item) for item in schema]
    elif isinstance(schema, str):
        return re.sub(r'https:\/\/web\.archive\.org\/web\/\d+\/', '', schema)
    else:
        return schema

def fetch_schema(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    schema_script = soup.find('script', {'type': 'application/ld+json'})
    if schema_script:
        schema = json.loads(schema_script.string)
        return preprocess_schema(schema)
    else:
        return None

def fetch_old_schema(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    schema_script = soup.find('script', {'type': 'application/ld+json'})
    if schema_script:
        schema = json.loads(schema_script.string)
        return preprocess_schema(schema)
    else:
        return None

def compare_schemas(current_schema, old_schema):
    diff = DeepDiff(current_schema, old_schema, ignore_order=True)
    return diff

def save_to_file(differences, filename):
    with open(filename, 'w') as file:
        file.write(json.dumps(differences, indent=4))

current_url = 'https://www.taskade.com/404'
old_url = 'https://www.taskade.com/500'

current_schema = fetch_schema(current_url)
old_schema = fetch_old_schema(old_url)

if current_schema:
    try:
        os.remove('current_schema.json')
    except FileNotFoundError:
        pass
    print("Current schema retrieved successfully. Saving to file...")
    save_to_file(current_schema, 'current_schema.json')
if old_schema:
    try:
        os.remove('old_schema.json')
    except FileNotFoundError:
        pass
    print("Old schema retrieved successfully. Saving to file...")
    save_to_file(old_schema, 'old_schema.json')

if current_schema and old_schema:
    differences = compare_schemas(current_schema, old_schema)
    if differences:
        try:
            os.remove('schema_differences.json')
        except FileNotFoundError:
            pass
        print("Differences found. Saving to file...")
        save_to_file(differences, 'schema_differences.json')
        print("Differences saved to schema_differences.json")
    else:
        print("The schemas are identical.")
else:
    if not current_schema:
        print("The current schema could not be retrieved.")
    if not old_schema:
        print("The old schema could not be retrieved.")
