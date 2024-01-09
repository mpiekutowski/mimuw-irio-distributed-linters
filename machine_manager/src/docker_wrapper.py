import docker

class DockerWrapper():
    def __init__(self):
        self.client = docker.from_env()

    def list(self):
        return map(lambda c: c.name, self.client.containers.list())