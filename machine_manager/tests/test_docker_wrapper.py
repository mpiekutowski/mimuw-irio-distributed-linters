from unittest.mock import Mock, patch
import docker.errors
import pytest
from src.docker_wrapper import DockerWrapper, DockerError, Image, Container

class MockClient:
    def __init__(self, networks, containers):
        self.networks = networks
        self.containers = containers

@pytest.fixture
def throwing_networks():
    mock_networks = Mock()
    mock_networks.get.side_effect = docker.errors.NotFound("some message")
    return mock_networks

@pytest.fixture
def well_behaved_networks():
    mock_networks = Mock()
    mock_specific_network = Mock()
    mock_specific_network.name = "linter_network"

    mock_networks.get.return_value = mock_specific_network
    return mock_networks

@pytest.fixture
def mock_container():
    mock_container = Mock()
    mock_container.id = "some_id"
    mock_container.attrs = {
        "NetworkSettings": {
            "Networks": {
                "linter_network": {
                    "IPAddress": "172.0.0.1"
                }
            }
        }
    }
    return mock_container

@pytest.fixture
def image():
    return Image(name="some_name", app_port=1234, env={"some": "env"})

def test_network_not_found(throwing_networks):
    with patch("docker.from_env", return_value=MockClient(throwing_networks, Mock())):
        with pytest.raises(DockerError):
            DockerWrapper()

def test_run_successful(image, mock_container, well_behaved_networks):
    mock_client = Mock()
    mock_client.containers = Mock()
    mock_client.containers.run.return_value = mock_container

    mock_client.networks = well_behaved_networks

    with patch("docker.from_env", return_value=mock_client):
        docker_wrapper = DockerWrapper()
        container = docker_wrapper.create(image)

        assert container == Container(id="some_id", address="172.0.0.1:1234")

        mock_client.containers.run.assert_called_once_with(
            image=image.name,
            environment=image.env,
            network=mock_client.networks.get.return_value.name,
            detach=True,
        )

def test_run_image_not_found(image, well_behaved_networks):
    mock_client = Mock()
    mock_client.containers = Mock()
    mock_client.containers.run.side_effect = docker.errors.ImageNotFound("some message")

    mock_client.networks = well_behaved_networks

    with patch("docker.from_env", return_value=mock_client):
        docker_wrapper = DockerWrapper()
        with pytest.raises(DockerError):
            docker_wrapper.create(image)

def test_run_api_error(image, well_behaved_networks):
    mock_client = Mock()
    mock_client.containers = Mock()
    mock_client.containers.run.side_effect = docker.errors.APIError("some message")

    mock_client.networks = well_behaved_networks

    with patch("docker.from_env", return_value=mock_client):
        docker_wrapper = DockerWrapper()
        with pytest.raises(DockerError):
            docker_wrapper.create(image)

def test_run_container_error(image, well_behaved_networks):
    mock_client = Mock()
    mock_client.containers = Mock()
    mock_client.containers.run.side_effect = docker.errors.ContainerError(None, None, None, None, None) 

    mock_client.networks = well_behaved_networks

    with patch("docker.from_env", return_value=mock_client):
        docker_wrapper = DockerWrapper()
        with pytest.raises(DockerError):
            docker_wrapper.create(image)
