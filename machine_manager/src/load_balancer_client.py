import requests

class LoadBalancerClient():
    def __init__(self, load_balancer_ip):
        self.load_balancer_ip = load_balancer_ip

    def _send_request(self, endpoint, body):
        url = f"{self.load_balancer_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}

        try:
            # TODO: uncomment when load balancer ready
            # requests.post(url, json=body, headers=headers)
            pass
        except requests.exceptions.RequestException as e:
            print(f"Error sending request to {url}: {e}")
        
    def add(self, lang, version, linter_ip):
        endpoint = '/add'
        body = {
            'lang': lang,
            'version': version,
            'uri': linter_ip
        }
        self._send_request(endpoint, body)

    def remove(self, linter_ip):
        endpoint = '/remove'
        body = {
            'uri': linter_ip
        }
        self._send_request(endpoint, body)

    

    

