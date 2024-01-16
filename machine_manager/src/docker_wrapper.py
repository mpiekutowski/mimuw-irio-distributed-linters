import docker
from dataclasses import dataclass


class DockerError(Exception):
    def __init__(self, message="Docker operation failed"):
        super().__init__(message)


@dataclass
class Image:
    name: str
    app_port: int
    env: dict


@dataclass
class Container:
    id: str
    host_port: int


class DockerWrapper:
    def __init__(self):
        self.client = docker.from_env()

    def create(self, image: Image):
        try:
            raw_container = self.client.containers.run(
                image=image.name,
                ports={
                    f"{image.app_port}/tcp": None # None means assign random free port on host
                },
                environment=image.env,
                detach=True,
            )

            # Reload is needed to get access to attributes like host port
            # See https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.Container
            raw_container.reload()
            host_port = raw_container.attrs["NetworkSettings"]["Ports"][f"{image.app_port}/tcp"][0]["HostPort"]

            return Container(id=raw_container.id, host_port=int(host_port))
        except docker.errors.ImageNotFound:
            raise DockerError(f"Container image not found")
        except docker.errors.APIError:
            raise DockerError(f"Internal docker error")
        except docker.errors.ContainerError:
            raise DockerError(f"Container exited with non-zero code")

    def remove(self, container: Container, timeout: int):
        try:
            self.client.containers.get(container.id).stop(timeout=timeout)
            self.client.containers.get(container.id).remove()
        except docker.errors.NotFound:
            raise DockerError(f"Could not find container")
        except docker.errors.APIError:
            raise DockerError(f"Internal docker error")
