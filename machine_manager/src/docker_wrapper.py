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
    address: str


class DockerWrapper:
    def __init__(self):
        self.client = docker.from_env()
        network_name = "linter_network"

        try:
            self.network = self.client.networks.get(network_name)
        except docker.errors.NotFound:
            raise DockerError(f"Network {network_name} not found")

    def create(self, image: Image):
        try:
            raw_container = self.client.containers.run(
                image=image.name,
                environment=image.env,
                network=self.network.name,
                detach=True,
            )

            # Reload is needed to get access to attributes like network addresses
            # See https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.Container
            raw_container.reload()
            address = raw_container.attrs["NetworkSettings"]["Networks"][self.network.name]["IPAddress"]
            address += ':' + str(image.app_port)

            return Container(id=raw_container.id, address=address)
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
