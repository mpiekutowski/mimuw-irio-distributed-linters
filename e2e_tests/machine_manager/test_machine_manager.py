import pytest
import requests
import json
import docker
import time

machine_manager_url = 'http://machine-manager:5000'


@pytest.fixture(autouse=True)
def cleanup_after_tests():
    yield
    delete_all_linters()

def MM_create(language, timeout=3):
        create_url = f'{machine_manager_url}/create'
        headers = {'Content-Type': 'application/json'}
        body = {
            'lang': language
        }
        return requests.post(create_url, json=body, headers=headers, timeout=timeout)

def MM_delete(linter_ip, timeout=3):
    delete_url = f'{machine_manager_url}/delete'
    headers = {'Content-Type': 'application/json'}
    body = {
        'ip': linter_ip
    }
    return requests.post(delete_url, json=body, headers=headers, timeout=timeout)

def MM_status(timeout=3):
    status_url = f'{machine_manager_url}/status'
    headers = {'Content-Type': 'application/json'}
    return requests.get(status_url, headers=headers, timeout=timeout)

def linter_lint(linter_ip, timeout=3, is_code_proper=True):
    lint_url = f'http://{linter_ip}/lint'
    headers = {'Content-Type': 'application/json'}
    if is_code_proper:
        code = 'sample code = good sample'
    else:
        code = 'sample code=bad sample'
    body = {
        'code': code
    }
    return requests.post(lint_url, json=body, headers=headers, timeout=timeout)

def delete_all_linters():
    response = MM_status()
    assert response.status_code == 200
    status_data = json.loads(response.text)
    linters = status_data.get('linters', [])
    for linter in linters:
        MM_delete(list(linter.keys())[0])
    response = MM_status()
    assert response.status_code == 200
    status_data = json.loads(response.text)
    assert not status_data.get('linters', [])

def get_response_field(response, key):
    response_data = json.loads(response.text)
    return response_data[key]

def check_request_count(linter_ip):
    status_response = MM_status()
    assert status_response.status_code == 200
    status_data = json.loads(status_response.text)
    linters_array = status_data.get('linters', [])
    print(linters_array)
    for linter in linters_array:
        if linter_ip in linter:
            return linter[linter_ip]['request_count']
    
    return 0


###################### TESTS ######################

def test_create_MM_delete():
    create_response = MM_create('java')
    assert create_response.status_code == 200

    create_response_data = json.loads(create_response.text)
    linter_ip = create_response_data['ip']

    status_response = MM_status()
    assert status_response.status_code == 200
    print(status_response.text)

    delete_response = MM_delete(linter_ip, timeout=30)
    assert delete_response.status_code == 200

    delete_response = MM_delete(linter_ip, timeout=30)
    assert delete_response.status_code != 200


def test_create_two_lang():
    java_response = MM_create('java')
    assert java_response.status_code == 200
    java_ip = get_response_field(java_response, 'ip')

    python_response = MM_create('python')
    assert python_response.status_code == 200
    python_ip = get_response_field(python_response, 'ip')

    status_response = MM_status()
    assert status_response.status_code == 200

    status_data = json.loads(status_response.text)
    linters_array = status_data.get('linters', [])
    assert any(java_ip in linter for linter in linters_array)
    assert any(python_ip in linter for linter in linters_array)

    for linter in linters_array:
        if java_ip in linter:
            assert linter[java_ip]['lang'] == 'java'
            assert linter[java_ip]['request_count'] == 0
        if python_ip in linter:
            assert linter[python_ip]['lang'] == 'python'
            assert linter[python_ip]['request_count'] == 0


def test_lint_status():
    response = MM_create('java')
    assert response.status_code == 200
    linter_ip = get_response_field(response, 'ip')
    assert(check_request_count(linter_ip) == 0)

    time.sleep(3) #toberemoved
    response = linter_lint(linter_ip)
    assert response.status_code == 200
    time.sleep(6) #FIXME: health_check_interval + 1
    assert(check_request_count(linter_ip) == 1)

    response = linter_lint(linter_ip, is_code_proper=False)
    assert response.status_code == 200
    time.sleep(6) #FIXME: health_check_interval + 1
    assert(check_request_count(linter_ip) == 2)

