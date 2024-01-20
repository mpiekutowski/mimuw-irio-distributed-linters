import requests
from json import dumps
import time

class LoadBalancerClient():
    def __init__(self, load_balancer_ip, secret_key):
        self.load_balancer_ip = load_balancer_ip
        self.secret_key = secret_key

    def _send_post_request(self, endpoint, body):
        url = f"http://{self.load_balancer_ip}{endpoint}"
        headers = {'Content-Type': 'application/json'}

        try:
            r = requests.post(url, json=body, headers=headers, timeout=3)
            if (r.status_code != 200):
                raise requests.exceptions.RequestException(f"Error sending request to load balancer {self.load_balancer_ip}{endpoint} (status code: {r.status_code})")
            pass
        except requests.exceptions.RequestException as e:
            raise e
        
    def add(self, lang, version, linter_ip):
        endpoint = '/add'
        body = {
            'lang': lang,
            'version': version,
            'uri': f"http://{linter_ip}",
            'secretKey': self.secret_key
        }
        return self._send_post_request(endpoint, body)

    def remove(self, linter_ip):
        endpoint = '/remove'
        body = {
            'uri': f"http://{linter_ip}",
            'secretKey': self.secret_key
        }
        return self._send_post_request(endpoint, body)
    
    def ratio(self, lang, versions):
        endpoint = '/ratio'
        body = {
            'lang': lang,
            'versionRatio': versions,
            'secretKey': self.secret_key
        }

        return self._send_post_request(endpoint, body)
    
    def wait_for_it(self, retries, interval):
        for _ in range(retries):
            time.sleep(interval)
            try:
                response = requests.get(f"http://{self.load_balancer_ip}/health")
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass

        return False