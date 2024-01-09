import docker

class Image():
    def __init__(self, lang, version, app_port=80, env=None):
        self.lang = lang
        self.version = version
        self.app_port = app_port
        self.env = env


class Container():
    def __init__(self, id, lang, version, host_port):
        self.id = id
        self.lang = lang
        self.version = version
        self.host_port = host_port


class DockerWrapper():
    def __init__(self):
        self.client = docker.from_env()

    def create(self, image):
        raw_container = self.client.containers.run(
            image=f'{image.lang}:{image.version}',
            ports={f'{image.app_port}/tcp': None},
            environment=image.env,
            detach=True
        )

        # Needed to refresh attributes such as host port
        # See https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.Container
        raw_container.reload()
        host_port = raw_container.attrs['NetworkSettings']['Ports'][f'{image.app_port}/tcp'][0]['HostPort']

        return Container(raw_container.id, image.lang, image.version, int(host_port))

    def remove(self, container, timeout):
        self.client.containers.get(container.id).stop(timeout=timeout)
        self.client.containers.get(container.id).remove()

    def list(self):
        pass