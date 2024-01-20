import pytest
import requests
import json
import docker

machine_manager_url = 'http://machine-manager:5000'


@pytest.fixture(autouse=True)
def cleanup_after_tests():
    yield
    delete_all_linters()

def create_linter(language, timeout=3):
        create_url = f"{machine_manager_url}/create"
        headers = {'Content-Type': 'application/json'}
        body = {
            "lang": language
        }
        return requests.post(create_url, json=body, headers=headers, timeout=timeout)

def delete_linter(linter_ip, timeout=3):
    delete_url = f"{machine_manager_url}/delete"
    headers = {'Content-Type': 'application/json'}
    body = {
        "ip": linter_ip
    }
    return requests.post(delete_url, json=body, headers=headers, timeout=timeout)

def check_status(timeout=3):
    status_url = f"{machine_manager_url}/status"
    headers = {'Content-Type': 'application/json'}
    return requests.get(status_url, headers=headers, timeout=timeout)

def delete_all_linters():
    response = check_status()
    assert response.status_code == 200
    status_data = json.loads(response.text)
    linters = status_data.get("linters", [])
    for linter in linters:
        delete_linter(list(linter.keys())[0])

    response = check_status()
    assert response.status_code == 200
    status_data = json.loads(response.text)
    assert not status_data.get("linters", [])

def get_response_field(response, key):
    response_data = json.loads(response.text)
    return response_data[key]


###################### TESTS ######################

def test_create_delete_linter():
    create_response = create_linter("java")
    assert create_response.status_code == 200

    create_response_data = json.loads(create_response.text)
    linter_ip = create_response_data['ip']

    status_response = check_status()
    assert status_response.status_code == 200
    print(status_response.text)

    delete_response = delete_linter(linter_ip, timeout=30)
    assert delete_response.status_code == 200

    delete_response = delete_linter(linter_ip, timeout=30)
    assert delete_response.status_code != 200


def test_create_two_lang():
    java_response = create_linter('java')
    assert java_response.status_code == 200
    java_ip = get_response_field(java_response, 'ip')

    python_response = create_linter('python')
    assert python_response.status_code == 200
    python_ip = get_response_field(python_response, 'ip')

    status_response = check_status()
    assert status_response.status_code == 200

    status_data = json.loads(status_response.text)
    linters_array = status_data.get('linters', [])
    assert any(java_ip in linters for linters in linters_array)
    assert any(python_ip in linters for linters in linters_array)

    for linter in linters_array:
        if java_ip in linter:
            assert linter[java_ip]['lang'] == 'java'
            assert linter[java_ip]['request_count'] == 0
        if python_ip in linter:
            assert linter[python_ip]['lang'] == 'python'
            assert linter[python_ip]['request_count'] == 0


def test_lint():
    response = create_linter("java")
    assert response.status_code == 200
    linter_ip = get_response_field(response, 'ip')

    response = check_status()
    assert response.status_code == 200
    print(json.loads(response.text))

    health_url = f"http://{linter_ip}/health"
    headers = {'Content-Type': 'application/json'}
    response = requests.get(health_url, headers=headers, timeout=3)

    assert response.status_code == 200
