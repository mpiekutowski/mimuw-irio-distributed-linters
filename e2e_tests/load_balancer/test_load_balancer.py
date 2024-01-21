import requests

LOAD_BALANCER_URL = 'http://load-balancer:8080'
SECRET_KEY = '123'
LANGS = ['java', 'python']
BASE_VERSION = '1.0'
EXPERIMENTAL_VERSION = '2.0'
REQUEST_COUNT = 100


def test_health():
    assert requests.get(LOAD_BALANCER_URL + '/health').status_code == 200


def test_no_linters():
    assert send_lint_request('java').status_code == 503
    assert send_lint_request('python').status_code == 503


def test_load_balancing():
    linter_ids = [1, 2]

    request_counts0 = [get_linters_request_count(lang, linter_ids) for lang in LANGS]

    # Add linters to RB arrays
    for i in linter_ids:
        for lang in LANGS:
            assert send_add_request(lang, i, BASE_VERSION).status_code == 200

    # Set ratio of load_balancing for BASE_VERSION only
    for lang in LANGS:
        assert send_ratio_request(lang, BASE_VERSION, REQUEST_COUNT).status_code == 200

    for i in range(REQUEST_COUNT):
        for lang in LANGS:
            assert send_lint_request(lang).status_code == 200

    request_counts1 = [get_linters_request_count(lang, linter_ids) for lang in LANGS]

    for i in range(len(request_counts0)):
        assert check_request_count(request_counts0[i], request_counts1[i], REQUEST_COUNT, len(linter_ids))

    # Remove first linter from each list
    for lang in LANGS:
        assert send_remove_request(lang, linter_ids[0]).status_code == 200

    for i in range(REQUEST_COUNT):
        for lang in LANGS:
            assert send_lint_request(lang).status_code == 200

    # Check if balancing after first deletion still works
    request_counts2 = [get_linters_request_count(lang, linter_ids) for lang in LANGS]

    for i in range(len(request_counts1)):
        assert request_counts1[i][0] == request_counts2[i][0]
        assert check_request_count(
            request_counts1[i][1:],
            request_counts2[i][1:],
            REQUEST_COUNT,
            len(linter_ids[1:])
        )

    # Cleanup
    for i in linter_ids[1:]:
        for lang in LANGS:
            assert send_remove_request(lang, i).status_code == 200


def test_ratio():
    linter_ids = [1, 2]
    exp_linter_ids = [3, 4]
    base_ratio = REQUEST_COUNT * 6 // 10
    exp_ratio = REQUEST_COUNT * 4 // 10

    request_counts0 = [get_linters_request_count(lang, linter_ids) for lang in LANGS]
    exp_request_counts0 = [get_linters_request_count(lang, exp_linter_ids) for lang in LANGS]

    # Add linters to RB arrays
    for i in linter_ids:
        for lang in LANGS:
            assert send_add_request(lang, i, BASE_VERSION).status_code == 200
    for i in exp_linter_ids:
        for lang in LANGS:
            assert send_add_request(lang, i, EXPERIMENTAL_VERSION).status_code == 200

    # Set ratio of load balancing between versions
    for lang in LANGS:
        assert send_ratio_request(
            lang,
            BASE_VERSION,
            base_ratio,
            EXPERIMENTAL_VERSION,
            exp_ratio
        ).status_code == 200

    for i in range(REQUEST_COUNT):
        for lang in LANGS:
            assert send_lint_request(lang).status_code == 200

    request_counts1 = [get_linters_request_count(lang, linter_ids) for lang in LANGS]
    exp_request_counts1 = [get_linters_request_count(lang, exp_linter_ids) for lang in LANGS]

    for i in range(len(request_counts0)):
        assert check_request_count(request_counts0[i], request_counts1[i], base_ratio, len(linter_ids))

    for i in range(len(exp_request_counts0)):
        assert check_request_count(exp_request_counts0[i], exp_request_counts1[i], exp_ratio, len(exp_linter_ids))

    # Remove first linter from each list
    for lang in LANGS:
        assert send_remove_request(lang, linter_ids[0]).status_code == 200
        assert send_remove_request(lang, exp_linter_ids[0]).status_code == 200

    for i in range(REQUEST_COUNT):
        for lang in LANGS:
            assert send_lint_request(lang).status_code == 200

    # Check if balancing after first deletion still works
    request_counts2 = [get_linters_request_count(lang, linter_ids) for lang in LANGS]
    exp_request_counts2 = [get_linters_request_count(lang, exp_linter_ids) for lang in LANGS]

    for i in range(len(request_counts1)):
        assert request_counts1[i][0] == request_counts2[i][0]
        assert check_request_count(
            request_counts1[i][1:],
            request_counts2[i][1:],
            base_ratio,
            len(linter_ids[1:])
        )

    for i in range(len(exp_request_counts1)):
        assert exp_request_counts1[i][0] == exp_request_counts2[i][0]
        assert check_request_count(
            exp_request_counts1[i][1:],
            exp_request_counts2[i][1:],
            exp_ratio,
            len(exp_linter_ids[1:])
        )

    # Cleanup
    for i in linter_ids[1:]:
        for lang in LANGS:
            assert send_remove_request(lang, i).status_code == 200

    for i in exp_linter_ids[1:]:
        for lang in LANGS:
            assert send_remove_request(lang, i).status_code == 200


#######################################################################################################################

def get_linters_request_count(lang, indices):
    return [get_linter_request_count(lang, i) for i in indices]


def get_linter_request_count(lang, index):
    url = get_linter_url(lang, index)
    return requests.get(url + '/health').json().get('requestCount')


def send_add_request(lang, index, version):
    payload = {
        "lang": lang,
        "version": version,
        "uri": get_linter_url(lang, index),
        "secretKey": SECRET_KEY
    }
    return requests.post(LOAD_BALANCER_URL + '/add', json=payload)


def send_remove_request(lang, index):
    payload = {
        "uri": get_linter_url(lang, index),
        "secretKey": SECRET_KEY
    }
    return requests.post(LOAD_BALANCER_URL + '/remove', json=payload)


def send_lint_request(lang):
    payload = {
        "code": "x = 42"
    }
    return requests.post(LOAD_BALANCER_URL + f'/lint/{lang}', json=payload)


def send_ratio_request(lang, v1, r1, v2="", r2=0):
    ratio = {
        v1: r1
    }
    if r2 != 0:
        ratio[v2] = r2

    payload = {
        "lang": lang,
        "versionRatio": ratio,
        "secretKey": SECRET_KEY
    }
    return requests.post(LOAD_BALANCER_URL + '/ratio', json=payload)


def check_request_count(initial, current, request_count, linter_count):
    return all(i + request_count / linter_count == c for i, c in zip(initial, current))


def get_linter_url(lang, index):
    return f'http://{lang}-linter-{index}'
