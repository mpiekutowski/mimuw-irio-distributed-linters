import docker

class DockerError(Exception):
    def __init__(self, message="Docker operation failed"):
        super().__init__(message)

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
        try:
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
        except docker.errors.ImageNotFound as e:
            raise DockerError(f'Container image not found')
        except docker.errors.APIError as e:
            raise DockerError(f'Internal docker error')
        except docker.errors.ContainerError as e:
            raise DockerError(f'Container exited with non-zero code')

    def remove(self, container, timeout):
        try:
            self.client.containers.get(container.id).stop(timeout=timeout)
            self.client.containers.get(container.id).remove()
        except docker.errors.NotFound as e:
            raise DockerError(f'Could not find container')
        except docker.errors.APIError as e:
            raise DockerError(f'Internal docker error')