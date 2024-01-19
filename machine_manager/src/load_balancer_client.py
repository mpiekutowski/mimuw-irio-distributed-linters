import requests

class LoadBalancerClient():
    def __init__(self, load_balancer_ip):
        self.load_balancer_ip = load_balancer_ip

    def _send_post_request(self, endpoint, body):
        url = f"{self.load_balancer_ip}{endpoint}"
        headers = {'Content-Type': 'application/json'}

        try:
            # TODO: uncomment when load balancer ready
            # r = requests.post(url, json=body, headers=headers, timeout=3)
            # if (r.status_code != 200):
            #     raise requests.exceptions.RequestException(f"Error sending request to load balancer {self.load_balancer_ip}{endpoint} (status code: {r.status_code})")
            pass
        except requests.exceptions.RequestException as e:
            raise e
        
    def add(self, lang, version, linter_ip):
        endpoint = '/add'
        body = {
            'lang': lang.str.lower(),
            'version': version,
            'uri': f"http://{linter_ip}"
        }
        return self._send_post_request(endpoint, body)

    def remove(self, linter_ip):
        endpoint = '/remove'
        body = {
            'uri': f"http://{linter_ip}"
        }
        return self._send_post_request(endpoint, body)
