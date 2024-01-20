from unittest.mock import patch
from threading import Lock
import time
import json

from health_check import HealthCheck, finish_health_check
from load_balancer_client import LoadBalancerClient

def mocked_load_balancer_remove(linter_ip):
    with patch('requests.post') as mock_post:
        mock_response = mock_post.return_value
        mock_response.status_code = 200

        return mock_response

def health_check_init(health_check_info = {}, mutex = Lock()):
    with patch.object(LoadBalancerClient, 'remove', side_effect=mocked_load_balancer_remove):
        load_balancer = LoadBalancerClient("http://load_balancer_ip")

        return HealthCheck(
            health_check_info=health_check_info,
            health_check_mutex=mutex,
            load_balancer=load_balancer,
            health_check_interval=0.5
        )

class TestHealthCheckInit:
    def test_start_and_join_thread(self):
        health_check_thread = health_check_init()
        health_check_thread.start()
        finish_health_check(health_check_thread)


class TestAddLinter:
    def test_add(self):
        with patch('requests.get') as mock_get:
            mock_response = mock_get.return_value
            mock_response.status_code = 200
            mock_response.text = json.dumps({
                "version": "1.0",
                "language": "java",
                "requestCount": 1
            })

            linter_ip1 = "1.1.1.1:1"
            health_check_info = {}
            health_check_info[linter_ip1] = dict(request_count=0, is_healthy=True)
            mutex = Lock()
            health_check_thread = health_check_init(health_check_info, mutex)
            health_check_thread.start()

            time.sleep(2 * health_check_thread.health_check_interval)

            finish_health_check(health_check_thread)

        
class TestRemoveLinter:
    def test_add_and_remove(self):
        with patch('requests.get') as mock_get:
            mock_response = mock_get.return_value
            mock_response.status_code = 200
            mock_response.text = json.dumps({
                "version": "1.0",
                "language": "java",
                "requestCount": 1
            })

            linter_ip1 = "1.1.1.1:1"
            health_check_info = {}
            health_check_info[linter_ip1] = dict(request_count=0, is_healthy=True)
            mutex = Lock()
            health_check_thread = health_check_init(health_check_info, mutex)
            health_check_thread.start()

            with mutex:
                health_check_info.pop(linter_ip1)

            time.sleep(2 * health_check_thread.health_check_interval)

            finish_health_check(health_check_thread)


class TestLint:
    def test_add_and_lint(self):
        with patch('requests.get') as mock_get:
            mock_response = mock_get.return_value
            mock_response.status_code = 200
            mock_response.text = json.dumps({
                "version": "1.0",
                "language": "java",
                "requestCount": 1
            })

            linter_ip1 = "1.1.1.1:1"
            health_check_info = {}
            health_check_info[linter_ip1] = dict(request_count=0, is_healthy=True)
            mutex = Lock()
            health_check_thread = health_check_init(health_check_info, mutex)
            health_check_thread.start()

            with mutex:
                health_check_info[linter_ip1] = dict(request_count=0, is_healthy=True)

            time.sleep(2 * health_check_thread.health_check_interval)
            request_count = health_check_info[linter_ip1]['request_count']

            finish_health_check(health_check_thread)

            assert request_count == 1


class TestBrokenLinter:
    def test_linter_broken_from_beginning(self):
        linter_ip1 = "1.1.1.1:1"
        health_check_info = {}
        health_check_info[linter_ip1] = dict(request_count=0, is_healthy=False)
        mutex = Lock()
        health_check_thread = health_check_init(health_check_info, mutex)
        health_check_thread.start()

        time.sleep(2 * health_check_thread.health_check_interval)
        linter_healthy = health_check_info[linter_ip1]['is_healthy']

        finish_health_check(health_check_thread)

        assert not linter_healthy


    def test_linter_break(self):
        with patch('requests.get') as mock_get:
            mock_response = mock_get.return_value
            mock_response.status_code = 500

            linter_ip1 = "1.1.1.1:1"
            health_check_info = {}
            health_check_info[linter_ip1] = dict(request_count=0, is_healthy=True)
            mutex = Lock()
            health_check_thread = health_check_init(health_check_info, mutex)
            health_check_thread.start()

            with mutex:
                health_check_info[linter_ip1] = dict(request_count=0, is_healthy=True)

            time.sleep(2 * health_check_thread.health_check_interval)
            linter_healthy = health_check_info[linter_ip1]['is_healthy']

            finish_health_check(health_check_thread)

            assert not linter_healthy
