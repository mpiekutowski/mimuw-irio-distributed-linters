from .docker_wrapper import Image
from typing import Optional, Dict, List
import json


class ImageStore:
    # TODO: add validation
    @staticmethod
    def from_json_file(file_path: str):
        with open(file_path) as f:
            full_json = json.load(f)

        images = dict()
        for lang in full_json.keys():
            images[lang] = dict()
            for image_json in full_json[lang]:
                version = image_json["version"]

                images[lang][version] = Image(
                    name=image_json["image_name"],
                    app_port=image_json["app_port"],
                    env=image_json["env"],
                )

        return ImageStore(images)

    def __init__(self, images: Dict[str, Dict[str, Image]]):
        self.images = images

    def get_image(self, lang: str, version: str) -> Optional[Image]:
        if lang not in self.images:
            return None
        if version not in self.images[lang]:
            return None
        return self.images[lang][version]
    
    def get_languages(self) -> List[str]:
        return list(self.images.keys())
    
    def get_versions(self, lang: str) -> List[str]:
        return list(self.images[lang].keys())
