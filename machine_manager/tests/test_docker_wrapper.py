from unittest.mock import Mock, patch
import docker.errors
import pytest
from src.docker_wrapper import DockerWrapper, DockerError, Image, Container

@pytest.fixture()
def mock_client():
    client = Mock()
    
    client.networks.get.return_value = Mock()
    client.networks.get.return_value.name = 'linter_network'

    return client

def test_network_not_found():
    client = Mock()
    client.networks.get.side_effect = docker.errors.NotFound('Network not found')

    with patch('docker.from_env', return_value=client):
        with pytest.raises(DockerError):
            DockerWrapper()

def test_run_success(mock_client):
    mock_container = Mock()
    mock_container.attrs = {
        "NetworkSettings": {
            "Networks": {
                "linter_network": {
                    "IPAddress": "172.0.0.1"
                }
            }
        }
    }
    mock_container.id = "some_id"
    mock_client.containers.run.return_value = mock_container

    with patch('docker.from_env', return_value=mock_client):
        docker_wrapper = DockerWrapper()

        image = Image(name='image_name', app_port=1234, env={"some": "env"})
        container = docker_wrapper.create(image)

        assert container.address == f"172.0.0.1:{image.app_port}"
        assert container.id == "some_id"

        mock_client.containers.run.assert_called_with(
            image=image.name,
            environment=image.env,
            network=mock_client.networks.get.return_value.name,
            detach=True,
        )

def test_run_api_error(mock_client):
    mock_client.containers.run.side_effect = docker.errors.APIError('API error')

    with patch('docker.from_env', return_value=mock_client):
        docker_wrapper = DockerWrapper()

        image = Image(name='image_name', app_port=1234, env={"some": "env"})

        with pytest.raises(DockerError):
            docker_wrapper.create(image)


def test_run_not_found(mock_client):
    mock_client.containers.run.side_effect = docker.errors.ImageNotFound('Image not found')

    with patch('docker.from_env', return_value=mock_client):
        docker_wrapper = DockerWrapper()

        image = Image(name='image_name', app_port=1234, env={"some": "env"})

        with pytest.raises(DockerError):
            docker_wrapper.create(image)

def test_run_container_error(mock_client):
    mock_client.containers.run.side_effect = docker.errors.ContainerError(None, None, None, None, None)

    with patch('docker.from_env', return_value=mock_client):
        docker_wrapper = DockerWrapper()

        image = Image(name='image_name', app_port=1234, env={"some": "env"})

        with pytest.raises(DockerError):
            docker_wrapper.create(image)

def test_remove_success(mock_client):
    mock_client.containers.get.return_value.stop.return_value = None

    with patch('docker.from_env', return_value=mock_client):
        docker_wrapper = DockerWrapper()
        container = Container(id="some_id", address="172.0.0.1:80")
        docker_wrapper.remove(container, timeout=1)

        mock_client.containers.get.assert_called_with(container.id)
        mock_client.containers.get.return_value.stop.assert_called_with(timeout=1)
        mock_client.containers.get.return_value.remove.assert_called_with()



def test_remove_api_error(mock_client):
    mock_client.containers.get.return_value.stop.side_effect = docker.errors.APIError('API error')

    with patch('docker.from_env', return_value=mock_client):
        docker_wrapper = DockerWrapper()
        container = Container(id="some_id", address="172.0.0.1:80")

        with pytest.raises(DockerError):
            docker_wrapper.remove(container, timeout=1)

def test_remove_not_found(mock_client):
    mock_client.containers.get.return_value.stop.side_effect = docker.errors.NotFound('Container not found')

    with patch('docker.from_env', return_value=mock_client):
        docker_wrapper = DockerWrapper()
        container = Container(id="some_id", address="172.0.0.1:80")

        with pytest.raises(DockerError):
            docker_wrapper.remove(container, timeout=1)
