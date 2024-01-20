import pytest
import requests
from json import dumps as dumps
import docker

machine_manager_url = 'http://machine-manager:5000'

def create_linter(language):
    create_url = f"{machine_manager_url}/create"
    headers = {'Content-Type': 'application/json'}
    body = {
        'lang': language
    }
    return requests.post(create_url, json=dumps(body), headers=headers, timeout=3)

def test_create_linter():
    response = create_linter("java")
    print(response.text)

    assert response.status_code == 200

