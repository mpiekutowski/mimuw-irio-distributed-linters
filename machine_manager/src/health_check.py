from threading import Thread, Event
import time
import sys
import requests

class HealthCheck(Thread):
    def __init__(self,  *args, **kwargs):
        super(HealthCheck, self).__init__(*args, **kwargs)
        self._stop_health_check = Event()

    def stop(self):
        self._stop_health_check.set()

    def stopped(self):
        return self._stop_health_check.is_set()
    
    def run(self):
        while not self.stopped():
            health_check_info, health_check_mutex = self._args
            self.health_check_loop(health_check_info, health_check_mutex)
            time.sleep(5)
            
    def health_check_loop(self, health_check_info, health_check_mutex):
        with health_check_mutex:
            health_check_items = health_check_info.items()
        for linter_ip, (request_count, is_healthy) in health_check_items:
            # TODO: get host from config?
            linter_url = f"http://{linter_ip}/health"
            print(linter_url, flush=True)
            response = requests.get(linter_url, timeout=3)

            if response.status_code == 200:
                print("Working")
                print(response.text)
            else:
                print(f"Error in request {response.status_code}", file=sys.stderr)

            # request_count = info.get('request_count')
            # is_healthy = info.get('is_healthy')
            # print(container_id, request_count, is_healthy, file=sys.stderr)


def finish_health_check(health_check_thread):
    health_check_thread.stop()
    health_check_thread.join()
