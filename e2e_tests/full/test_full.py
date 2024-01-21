import pytest
import requests
import json
import time

machine_manager_url = 'http://machine-manager:5000'
load_balancer_url = 'http://load-balancer:8080'

HEALTH_CHECK_INTERVAL = 5
UPDATE_STEPS = [1, 5, 10, 50, 100]

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
    print(f"Deleting linter {linter_ip}")

    delete_url = f"{machine_manager_url}/delete"
    headers = {'Content-Type': 'application/json'}
    body = {
        "ip": linter_ip
    }
    response = requests.post(delete_url, json=body, headers=headers, timeout=timeout)
    print(response.text)
    return response

def init_update(language, version, timeout=3):
    init_update_url = f"{machine_manager_url}/init-update"
    headers = {'Content-Type': 'application/json'}
    body = {
        "lang": language,
        "version": version
    }
    return requests.post(init_update_url, json=body, headers=headers, timeout=timeout)

def update(language, timeout=3):
    update_url = f"{machine_manager_url}/update"
    headers = {'Content-Type': 'application/json'}
    body = {
        "lang": language
    }
    return requests.post(update_url, json=body, headers=headers, timeout=timeout)

def check_status(timeout=3):
    status_url = f"{machine_manager_url}/status"
    headers = {'Content-Type': 'application/json'}
    return requests.get(status_url, headers=headers, timeout=timeout)

def delete_all_linters():
    response = check_status()
    assert response.status_code == 200
    status_data = json.loads(response.text)
    linters = status_data.get("linters", [])

    while len(linters) != 0:
        delete_linter(list(linters[0].keys())[0])
        time.sleep(3)

        response = check_status()
        assert response.status_code == 200
        status_data = json.loads(response.text)
        linters = status_data.get("linters", [])

    response = check_status()
    assert response.status_code == 200
    status_data = json.loads(response.text)
    assert status_data["linters"] == []

def get_response_field(response, key):
    response_data = json.loads(response.text)
    return response_data[key]

def lint(language, code, timeout=3):
    lint_url = f"{load_balancer_url}/lint/{language}"
    headers = {'Content-Type': 'application/json'}
    body = {
        "code": code
    }
    return requests.post(lint_url, json=body, headers=headers, timeout=timeout)


def test_full_response():
    response = create_linter("python")
    assert response.status_code == 200
    assert get_response_field(response, "status") == "ok"
    linter_ip = get_response_field(response, "ip")

    response = lint("python", "print('hello world')")
    assert response.status_code == 200
    assert get_response_field(response, "result") == True

    response = delete_linter(linter_ip)
    assert response.status_code == 200
    assert get_response_field(response, "status") == "ok"

    response = check_status()
    assert response.status_code == 200
    status_data = json.loads(response.text)
    assert status_data["linters"] == []

    response = lint("python", "print('hello world')")
    assert response.status_code == 200
    assert response.text == "No available linters"

def test_status_request_count():
    response = create_linter("python")
    assert response.status_code == 200
    assert get_response_field(response, "status") == "ok"
    linter_ip = get_response_field(response, "ip")
    
    response = check_status()
    assert response.status_code == 200
    status_data = json.loads(response.text)
    assert status_data["linters"] != []

    linter_status = status_data["linters"][0][linter_ip]
    assert linter_status["request_count"] == 0

    for _ in range(10):
        response = lint("python", "print('hello world')")
        assert response.status_code == 200
        assert get_response_field(response, "result") == True

    # Check for health check info to be updated
    time.sleep(2 * HEALTH_CHECK_INTERVAL)

    response = check_status()
    assert response.status_code == 200
    status_data = json.loads(response.text)
    assert status_data["linters"] != []

    linter_status = status_data["linters"][0][linter_ip]
    assert linter_status["request_count"] == 10

def check_request_count_delta(before_array, after_array, old_version, new_version, update_step, request_count):
    linter_count = len(before_array)
    old_version_count = 0
    new_version_count = 0

    for linter in before_array:
        linter_ip = list(linter.keys())[0]

        if linter[linter_ip]["version"] == old_version:
            old_version_count += 1
        elif linter[linter_ip]["version"] == new_version:
            new_version_count += 1

    assert old_version_count + new_version_count == linter_count

    if old_version_count == 0:
        old_version_target_delta = 0
    else:
        old_version_target_delta = (request_count * (100 - update_step) / 100) / old_version_count

    new_version_target_delta = (request_count * update_step / 100) / new_version_count

    for linter_before in before_array:
        linter_ip = list(linter_before.keys())[0]

        linter_after = None
        for linter in after_array:
            if list(linter.keys())[0] == linter_ip:
                linter_after = linter
                break

        assert linter_after != None

        if linter_before[linter_ip]["version"] == old_version:
            request_count_delta = linter_after[linter_ip]["request_count"] - linter_before[linter_ip]["request_count"]
            assert request_count_delta == old_version_target_delta
        elif linter_before[linter_ip]["version"] == new_version:
            request_count_delta = linter_after[linter_ip]["request_count"] - linter_before[linter_ip]["request_count"]
            assert request_count_delta == new_version_target_delta

def test_machine_and_traffic_ratio():
    response = init_update("python", "2.0")
    assert response.status_code == 200
    # assert get_response_field(response, "status") == "ok"

    for _ in range(2):
        response = create_linter("python")
        assert response.status_code == 200
        assert get_response_field(response, "status") == "ok"

    REQUEST_COUNT = 100
    for step in UPDATE_STEPS:
        time.sleep(2 * HEALTH_CHECK_INTERVAL)

        response = check_status()
        assert response.status_code == 200
        status_data = json.loads(response.text)
        before_array = status_data["linters"]
        assert len(before_array) == 2

        for _ in range(REQUEST_COUNT):
            response = lint("python", "print('hello world')\n")
            assert response.status_code == 200
            assert get_response_field(response, "result") == True

        time.sleep(2 * HEALTH_CHECK_INTERVAL)

        response = check_status()
        assert response.status_code == 200
        status_data = json.loads(response.text)
        after_array = status_data["linters"]
        assert len(after_array) == 2

        check_request_count_delta(before_array, after_array, "1.0", "2.0", step, REQUEST_COUNT)

        response = update("python")
        if step != 100:
            assert response.status_code == 200
            assert get_response_field(response, "status") == "ok"
        else:
            assert response.status_code == 400
            assert get_response_field(response, "status") == "error"

    # Bring back version to 1.0 so other tests can run
    response = init_update("python", "1.0")
    assert response.status_code == 200
    # assert get_response_field(response, "status") == "ok"

    for step in UPDATE_STEPS:
        response = update("python")
        
        if step != 100:
            assert response.status_code == 200
            assert get_response_field(response, "status") == "ok"
        else:
            assert response.status_code == 400
            assert get_response_field(response, "status") == "error"
