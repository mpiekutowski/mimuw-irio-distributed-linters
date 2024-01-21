import pytest
import requests
import json
import docker
import time
import subprocess

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

def MM_init_update(lang, version, timeout=3):
    init_update_url = f'{machine_manager_url}/init-update'
    headers = {'Content-Type': 'application/json'}
    body = {
        'lang': lang,
        'version': version
    }
    return requests.post(init_update_url, json=body, headers=headers, timeout=timeout)

def MM_update(lang, timeout=3):
    update_url = f'{machine_manager_url}/update'
    headers = {'Content-Type': 'application/json'}
    body = {
        'lang': lang
    }
    return requests.post(update_url, json=body, headers=headers, timeout=timeout)

def MM_rollback(lang, timeout=3):
    rollback_url = f'{machine_manager_url}/rollback'
    headers = {'Content-Type': 'application/json'}
    body = {
        'lang': lang,
    }
    return requests.post(rollback_url, json=body, headers=headers, timeout=timeout)

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
    linters = get_linters_array_from_status()
    while linters:
        MM_delete(next(iter(linters.pop(0).keys())))
        linters = get_linters_array_from_status()
    linters = get_linters_array_from_status()
    assert not linters, "Not all linters were deleted after the test"

def get_response_field(response, key):
    response_data = json.loads(response.text)
    return response_data[key]

def get_linters_array_from_status():
    status_response = MM_status()
    assert status_response.status_code == 200
    status_data = json.loads(status_response.text)
    return status_data.get('linters', [])

def get_linter_from_status(linter_ip):
    linters_array = get_linters_array_from_status()
    for linter in linters_array:
        if linter_ip in linter:
            return linter[linter_ip]
    return None


###################### TESTS ######################

# FIXME: docker ps
# Created machine is present in `docker ps` output
# def test_create_MM():
#     create_data = create_response = MM_create('java')

#     command = "docker ps"
#     result = subprocess.run(command, shell=True, capture_output=True, text=True)
#     # assert result.returncode == 0, f"Command '{command}' failed with output: {result.stderr}"
#     # assert "CONTAINER ID" in result.stdout, "Expected header not found in 'docker ps' output"
#     # assert "your_container_name" in result.stdout, "Expected container not found in 'docker ps' output"
#     # print(result.stdout)

#     linter_ip = create_data['ip']

#     status_response = MM_status()
#     assert status_response.status_code == 200


# FIXME: docker ps
# Deleted machine is no longer present in `docker ps` output
# def test_delete_MM():
#     create_response = MM_create('java')
#     assert create_response.status_code == 200

#     create_response_data = json.loads(create_response.text)
#     linter_ip = create_response_data['ip']

#     status_response = MM_status()
#     assert status_response.status_code == 200

#     delete_response = MM_delete(linter_ip, timeout=30)
#     assert delete_response.status_code == 200

#     delete_response = MM_delete(linter_ip, timeout=30)
#     assert delete_response.status_code != 200


# Delete existing linter returns 200 and otherwise not
# def test_create_delete():
#     create_response = MM_create('java')
#     assert create_response.status_code == 200
#     linter_ip = get_response_field(create_response, 'ip')

#     status_response = MM_status()
#     assert status_response.status_code == 200

#     delete_response = MM_delete(linter_ip, timeout=30)
#     assert delete_response.status_code == 200

#     delete_response = MM_delete(linter_ip, timeout=30)
#     assert delete_response.status_code != 200


# Linters are created with proper languages
def test_create_two_lang():
    java_response = MM_create('java')
    assert java_response.status_code == 200
    java_ip = get_response_field(java_response, 'ip')

    python_response = MM_create('python')
    assert python_response.status_code == 200
    python_ip = get_response_field(python_response, 'ip')

    linters_array = get_linters_array_from_status()
    assert any(java_ip in linter for linter in linters_array)
    assert any(python_ip in linter for linter in linters_array)

    for linter in linters_array:
        if java_ip in linter:
            assert linter[java_ip]['lang'] == 'java'
            assert linter[java_ip]['request_count'] == 0
        if python_ip in linter:
            assert linter[python_ip]['lang'] == 'python'
            assert linter[python_ip]['request_count'] == 0


# Health check updates linters' requests count
def test_lint_request_count():
    response = MM_create('java')
    assert response.status_code == 200
    linter_ip = get_response_field(response, 'ip')
    assert get_linter_from_status(linter_ip).get('request_count', -1) == 0

    response = linter_lint(linter_ip)
    assert response.status_code == 200
    time.sleep(6) #FIXME: health_check_interval + 1
    assert get_linter_from_status(linter_ip).get('request_count', -1) == 1

    response = linter_lint(linter_ip, is_code_proper=False)
    assert response.status_code == 200
    time.sleep(6) #FIXME: health_check_interval + 1

    assert get_linter_from_status(linter_ip).get('request_count', -1) == 2

    response = linter_lint(linter_ip, is_code_proper=False)
    response = linter_lint(linter_ip, is_code_proper=False)
    response = linter_lint(linter_ip, is_code_proper=False)
    assert response.status_code == 200
    time.sleep(6) #FIXME: health_check_interval + 1
    assert get_linter_from_status(linter_ip).get('request_count', -1) == 5


# Machine manager determines created machine version
def test_update_create_version():
    for _ in range(10):
        response = MM_create('java')
        assert response.status_code == 200

    response = MM_init_update('java', '2.0')
    assert response.status_code == 200
    
    response = MM_create('java')
    assert response.status_code == 200

    linters_array = get_linters_array_from_status()
    v1_cnt = sum(1 for linter in linters_array for ip in linter if linter[ip]['version'] == '1.0')
    v2_cnt = sum(1 for linter in linters_array for ip in linter if linter[ip]['version'] == '2.0')

    assert v1_cnt == 10 and v2_cnt == 1


# Machine manager keeps machine ratio during the update
# Call /create/{lang} with chosen language 2 times, wait for response each time.
# Call /init-update/{version, lang} to start updating to a new version.
# Call /status.
# Check:
# For the current update ratio in [0.1%, 1%, 10%, 50%] there should be 1 machine on the old version, 1 on the new version.
# For the current update ratio 100%, both machines should be on the new version.
#  Repeat steps 3-4 until we hit update ratio 100% (check MM config to keep track of ratios).



