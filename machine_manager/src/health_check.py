from threading import Thread, Event
import time
import requests
import json
import _thread


def finish_health_check(health_check_thread):
    health_check_thread.stop()
    health_check_thread.join()

class HealthCheckTerminatinError(Exception):
    pass

class HealthCheck(Thread):
    def __init__(self, health_check_info, health_check_mutex, load_balancer, health_check_interval, *args, **kwargs):
        super(HealthCheck, self).__init__(*args, **kwargs)
        self._stop_health_check = Event()
        self.health_check_info = health_check_info
        self.health_check_mutex = health_check_mutex
        self.load_balancer = load_balancer
        self.health_check_interval = health_check_interval

    def stop(self):
        self._stop_health_check.set()

    def stopped(self):
        return self._stop_health_check.is_set()
    
    def run(self):
        try:
            while not self.stopped():
                self.health_check_loop()
                time.sleep(self.health_check_interval)
        except HealthCheckTerminatinError as e:
            _thread.interrupt_main()
            raise e
            
    def health_check_loop(self):
        with self.health_check_mutex:
            health_check_items = self.health_check_info.items()
        for linter_ip, data in health_check_items:
            if not data['is_healthy']:
                continue

            linter_url = f"http://{linter_ip}/health"
            response = requests.get(linter_url, timeout=3)

            linter_health = response.status_code == 200
            request_count_updated = data['request_count']

            if response.status_code == 200:
                parsed_response = json.loads(response.text)
                request_count_updated = parsed_response['requestCount']
            else:
                try:
                    self.load_balancer.remove(linter_ip)
                except requests.exceptions.RequestException as e:
                    raise HealthCheckTerminatinError(e)

            with self.health_check_mutex:
                self.health_check_info[linter_ip] = dict(request_count=request_count_updated, is_healthy=linter_health)
