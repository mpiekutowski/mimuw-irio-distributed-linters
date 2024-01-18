import json
import pytest
from src.image_store import ImageStore
from src.docker_wrapper import Image
import tempfile
import os

@pytest.fixture
def temp_json_file():
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    with open(temp_file.name, 'w') as f:
        json.dump({
        "java": [
            {
                "version": "1.0",
                "image_name": "java:1.0",
                "app_port": 8080,
                "env": {"LANGUAGE": "java"}
            },
            {
                "version": "2.0",
                "image_name": "java:2.0",
                "app_port": 8081,
                "env": {"LANGUAGE": "java", "PROCESSING_TIME": 5}
            }
        ],
        "python": [
            {
                "version": "1.0",
                "image_name": "python:1.0",
                "app_port": 8000,
                "env": {"LANGUAGE": "python"}
            }
        ]
    }, f)
    yield temp_file.name
    os.remove(temp_file.name)

def test_nonexistent_json():
    with pytest.raises(FileNotFoundError):
        ImageStore.from_json_file("nonexistent.json")

def test_get_languages(temp_json_file):
    image_store = ImageStore.from_json_file(temp_json_file)

    assert sorted(image_store.get_languages()) == sorted(["java", "python"])

def test_get_versions(temp_json_file):
    image_store = ImageStore.from_json_file(temp_json_file)

    assert sorted(image_store.get_versions("java")) == sorted(["1.0", "2.0"])
    assert sorted(image_store.get_versions("python")) == sorted(["1.0"])
    assert image_store.get_versions("nonexistent") is None

def test_get_images(temp_json_file):
    image_store = ImageStore.from_json_file(temp_json_file)

    java_10_image = Image(name="java:1.0", app_port=8080, env={"LANGUAGE": "java"})
    assert image_store.get_image("java", "1.0") == java_10_image

    java_20_image = Image(name="java:2.0", app_port=8081, env={"LANGUAGE": "java", "PROCESSING_TIME": 5})
    assert image_store.get_image("java", "2.0") == java_20_image

    python_10_image = Image(name="python:1.0", app_port=8000, env={"LANGUAGE": "python"})
    assert image_store.get_image("python", "1.0") == python_10_image

    assert image_store.get_image("java", "nonexistent") is None
    assert image_store.get_image("nonexistent", "1.0") is None
    assert image_store.get_image("nonexistent", "nonexistent") is None