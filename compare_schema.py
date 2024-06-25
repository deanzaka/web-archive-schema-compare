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

current_url = 'https://yourcurrentwebsite.com'
old_url = 'https://web.archive.org/web/20220101010101/http://youroldwebsite.com'

current_schema = fetch_schema(current_url)
old_schema = fetch_old_schema(old_url)

if current_schema and old_schema:
    print("Schemas retrieved successfully. Saving to file...")
    save_to_file(current_schema, 'current_schema.json')
    save_to_file(old_schema, 'old_schema.json')
    differences = compare_schemas(current_schema, old_schema)
    if differences:
        print("Differences found. Saving to file...")
        save_to_file(differences, 'schema_differences.json')
        print("Differences saved to schema_differences.json")
    else:
        print("The schemas are identical.")
else:
    print("One of the schemas could not be retrieved.")
