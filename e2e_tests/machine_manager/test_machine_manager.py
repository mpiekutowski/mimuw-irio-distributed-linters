import pytest
import requests
import json
import time
import subprocess
import math

machine_manager_url = 'http://machine-manager:5000'

HEALTH_CHECK_INTERVAL = 5
UPDATE_STEPS = [1, 5, 10, 50, 100]
LINTERS_VERSIONS = ['1.0', '1.1', '1.2', '2.0']

@pytest.fixture(autouse=True)
def cleanup_after_tests():
    yield
    delete_all_linters()
    finish_update()

def MM_create(language, timeout=3):
    create_url = f'{machine_manager_url}/create'
    headers = {'Content-Type': 'application/json'}
    body = {
        'lang': language
    }
    return requests.post(create_url, json=body, headers=headers, timeout=timeout)

def MM_delete(linter_ip, timeout=5):
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

def linter_lint(linter_ip, timeout=3, code='sample code = good sample'):
    lint_url = f'http://{linter_ip}/lint'
    headers = {'Content-Type': 'application/json'}
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

def finish_update_lang_version(lang, version):
    status_code = 200
    MM_init_update(lang=lang, version=version)
    while status_code == 200:
        r = MM_update(lang=lang)
        status_code = r.status_code

def finish_update():
    for version in reversed(LINTERS_VERSIONS):
        finish_update_lang_version('java', version)
        finish_update_lang_version('python', version)

def get_response_field(response, key):
    response_data = json.loads(response.text)
    return response_data[key]

def get_linters_array_from_status():
    status_response = MM_status()
    assert status_response.status_code == 200, status_response.text
    status_data = json.loads(status_response.text)
    return status_data.get('linters', [])

def get_linter_from_status(linter_ip):
    linters_array = get_linters_array_from_status()
    for linter in linters_array:
        if linter_ip in linter:
            return linter[linter_ip]
    return None

def count_linters_version(linters, lang, version):
    return sum(1 for linter in linters for ip in linter
               if linter[ip]['lang'] == lang and linter[ip]['version'] == version)


###################### TESTS ######################

# Created machine is present in `docker ps` output
def test_create_MM():
    create_response = MM_create('java')
    assert create_response.status_code == 200, create_response.text
    create_data = json.loads(create_response.text)
    linter_ip = create_data['ip']

    command = "docker ps"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    assert result.returncode == 0, f"Command '{command}' failed with output: {result.stderr}"
    assert 'linter:1.0' in result.stdout

    assert get_linter_from_status(linter_ip)


# Created machine is present in `docker ps` output
def test_delete_MM():
    create_response = MM_create('java')
    assert create_response.status_code == 200, create_response.text
    create_data = json.loads(create_response.text)
    linter_ip = create_data['ip']

    delete_response = MM_delete(linter_ip)
    assert delete_response.status_code == 200, delete_response.text

    command = "docker ps"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    assert result.returncode == 0, f"Command '{command}' failed with output: {result.stderr}"
    assert 'linter:1.0' not in result.stdout

    assert not get_linter_from_status(linter_ip)


# Delete existing linter returns 200 and otherwise not
def test_create_delete():
    create_response = MM_create('java')
    assert create_response.status_code == 200
    linter_ip = get_response_field(create_response, 'ip')

    status_response = MM_status()
    assert status_response.status_code == 200, status_response.text

    delete_response = MM_delete(linter_ip)
    assert delete_response.status_code == 200, delete_response.text

    delete_response = MM_delete(linter_ip)
    assert delete_response.status_code != 200, delete_response.text


# Linters are created with proper languages
def test_create_two_lang():
    java_response = MM_create('java')
    assert java_response.status_code == 200, java_response.text
    java_ip = get_response_field(java_response, 'ip')

    python_response = MM_create('python')
    assert python_response.status_code == 200, python_response.text
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
    assert response.status_code == 200, response.text
    time.sleep(HEALTH_CHECK_INTERVAL + 1)
    assert get_linter_from_status(linter_ip).get('request_count', -1) == 1

    response = linter_lint(linter_ip, code='sample code=bad sample')
    assert response.status_code == 200, response.text
    time.sleep(HEALTH_CHECK_INTERVAL + 1)

    assert get_linter_from_status(linter_ip).get('request_count', -1) == 2

    response = linter_lint(linter_ip)
    response = linter_lint(linter_ip)
    response = linter_lint(linter_ip)
    assert response.status_code == 200, response.text
    time.sleep(HEALTH_CHECK_INTERVAL + 1)
    assert get_linter_from_status(linter_ip).get('request_count', -1) == 5


# Machine manager determines created machine version
def test_update_create_version():
    for _ in range(10):
        response = MM_create('java')
        assert response.status_code == 200, response.text

    response = MM_init_update('java', '2.0')
    assert response.status_code == 200, response.text
    
    response = MM_create('java')
    assert response.status_code == 200, response.text

    linters_array = get_linters_array_from_status()
    v1_cnt = count_linters_version(linters=linters_array, lang='java', version='1.0')
    v2_cnt = count_linters_version(linters=linters_array, lang='java', version='2.0')

    assert v1_cnt == 10 and v2_cnt == 1


# Machine manager keeps machine ratio during the update
def test_keep_machine_ratio():
    response = MM_create('java')
    assert response.status_code == 200, response.text
    response = MM_create('java')
    assert response.status_code == 200, response.text
    response = MM_init_update('java', '2.0')
    assert response.status_code == 200, response.text

    for ratio in UPDATE_STEPS:
        linters = get_linters_array_from_status()
        v1_cnt = count_linters_version(linters=linters, lang='java', version='1.0')
        v2_cnt = count_linters_version(linters=linters, lang='java', version='2.0')
        if ratio != 100:
            assert v1_cnt == 1
            assert v2_cnt == 1
            response = MM_update('java')
            assert response.status_code == 200, response.text
        else:
            assert v1_cnt == 0
            assert v2_cnt == 2
        

# Machine manager keeps the machine update ratio during the update for a more complicated number of machines
def test_keep_machine_ratio_more_machines():
    linters_number = 11
    for _ in range(linters_number):
        response = MM_create('java')
        assert response.status_code == 200, response.text
    response = MM_init_update('java', '2.0')
    assert response.status_code == 200, response.text

    for ratio in UPDATE_STEPS:
        linters = get_linters_array_from_status()
        v1_cnt = count_linters_version(linters=linters, lang='java', version='1.0')
        v2_cnt = count_linters_version(linters=linters, lang='java', version='2.0')
        assert v2_cnt == math.ceil(linters_number * ratio / 100)
        assert v1_cnt == linters_number - v2_cnt

        if ratio != 100:
            response = MM_update('java', timeout=30)
            assert response.status_code == 200, response.text


# Roundtrip create/delete: final status same as initial
def test_create_delete_roundtrip():
    assert not get_linters_array_from_status()

    linter_ips = []
    for _ in range(10):
        response = MM_create('java')
        assert response.status_code == 200, response.text
        response_data = json.loads(response.text)
        linter_ips.append(response_data['ip'])

    for ip in linter_ips:
        response = MM_delete(ip)
        assert response.status_code == 200, response.text

    assert not get_linters_array_from_status()


# Roundtrip update/rollback: final status same as initial
def test_update_rollback_roundtrip():
    linters_number = 5
    for _ in range(linters_number):
        response = MM_create('java')
        assert response.status_code == 200, response.text
    response = MM_init_update('java', '2.0')
    assert response.status_code == 200, response.text

    linters_array = get_linters_array_from_status()
    v1_before = count_linters_version(linters_array, 'java', '1.0')
    v2_before = count_linters_version(linters_array, 'java', '2.0')

    for _ in UPDATE_STEPS[:-2]:
        response = MM_update('java', timeout=30)
        assert response.status_code == 200, response.text

    for _ in UPDATE_STEPS[1:-1][::-1]:
        response = MM_rollback('java', timeout=30)
        assert response.status_code == 200, response.text

    linters_array = get_linters_array_from_status()
    v1_after = count_linters_version(linters_array, 'java', '1.0')
    v2_after = count_linters_version(linters_array, 'java', '2.0')

    assert v1_before == v1_after and v2_before == v2_after
        