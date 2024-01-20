import pytest
import requests
from json import dumps as dumps
import docker

machine_manager_url = 'http://machine-manager:5000'

def test_status():
    status_response = requests.get(machine_manager_url + '/status')

    assert status_response.status_code == 200