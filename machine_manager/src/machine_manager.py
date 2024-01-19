from docker_wrapper import DockerWrapper, Image, DockerError, Container
from image_store import ImageStore
from version_tracker import VersionTracker, Readjustment
from typing import List
from threading import Lock
from dataclasses import dataclass

@dataclass
class Linter:
    lang: str
    version: str
    container: Container

@dataclass
class Config:
    timeout: int
    load_balancer_ip: str
    health_check_interval: int

class MachineManager:
    def __init__(self, image_store: ImageStore, update_steps: List[float], config: Config):
        self.image_store = image_store
        self.docker = DockerWrapper()
        self.version_trackers = {}
        self.linters = []
        self.health_check_info = {} # dict(container_ip, dict(request_count, is_healthy))
        self.health_check_mutex = Lock()
        self.config = config

        for lang in image_store.get_languages():
            self.version_trackers[lang] = VersionTracker(
                initial_version="1.0", 
                update_steps=update_steps
            )

    def _create_linter(self, lang: str, version: str, image: Image) -> (Linter, Readjustment):
        try:
            container = self.docker.create(image)
        except DockerError as e:
            raise RuntimeError(e)
        
        linter = Linter(lang=lang, version=version, container=container)
        self.linters.append(linter)
        with self.health_check_mutex:
            self.health_check_info[linter.container.address] = dict(request_count=0, is_healthy=True)
        readjustment = self.version_trackers[lang].add(version)

        return linter, readjustment
    
    def _remove_linter(self, linter: Linter) -> Readjustment:
        ip = linter.container.address

        try:
            self.docker.remove(linter.container, timeout=self.config.timeout)
        except DockerError as e:
            raise RuntimeError(e)
        
        self.linters.remove(linter)
        with self.health_check_mutex:
            self.health_check_info.pop(ip)
        readjustment = self.version_trackers[linter.lang].remove(linter.version)

        return readjustment
    
    def _replace_containers(self, lang: str, readjustment: Readjustment):
        if readjustment is None:
            return

        from_version = readjustment.from_version
        to_version = readjustment.to_version
        count = readjustment.count

        for linter in self.linters:
            if linter.lang == lang and linter.version == from_version:
                self._remove_linter(linter)
                self._create_linter(lang, to_version, self.image_store.get_image(lang, to_version))
                count -= 1

            if count == 0:
                break

        if count != 0:
            raise RuntimeError(f'Internal error: readjustment count mismatch: {count}')

    def create_linter(self, lang: str) -> Linter:
        if lang not in self.version_trackers.keys():
            raise ValueError(f'Unsupported lang: {lang}')
        
        version = self.version_trackers[lang].determine_version()
        image = self.image_store.get_image(lang, version)

        if image is None:
            # This should never happen, as versions in image store and version tracker are the same
            # Some kind of internal error
            raise RuntimeError(f'Internal error: no image for lang: {lang}, version: {version}')
        
        linter, readjustment = self._create_linter(lang, version, image)
        
        if readjustment is not None:
            # VersionTracker guarantees that adding a container with version
            # determined by it will not cause any readjustment
            # So this should never happen too
            raise RuntimeError(f'Internal error: readjustment needed for lang: {lang}, version: {version}')

        return linter
    
    def delete_linter(self, address: str):
        target_linter = None

        for linter in self.linters:
            if linter.container.address == address:
                target_linter = linter
                break

        if target_linter is None:
            raise ValueError(f'No linter with address: {address}')
        
        readjustment = self._remove_linter(target_linter)

        if readjustment is not None:
            self._replace_containers(target_linter.lang, readjustment)

    def init_update(self, lang: str, version: str):
        if lang not in self.version_trackers.keys():
            raise ValueError(f'Unsupported lang: {lang}')
        
        if version not in self.image_store.get_versions(lang):
            raise ValueError(f'Unsupported version: {version}')

        readjustment = self.version_trackers[lang].start_update(version)
        self._replace_containers(lang, readjustment)

        if self.version_trackers[lang].update_status().progress == 100:
            self.version_trackers[lang].finish_update()

    def update(self, lang: str):
        if lang not in self.version_trackers.keys():
            raise ValueError(f'Unsupported lang: {lang}')
        
        readjustment = self.version_trackers[lang].move_to_next_step()
        self._replace_containers(lang, readjustment)

        if self.version_trackers[lang].update_status().progress == 100:
            self.version_trackers[lang].finish_update()

    def rollback(self, lang: str):
        if lang not in self.version_trackers.keys():
            raise ValueError(f'Unsupported lang: {lang}')

        readjustment = self.version_trackers[lang].move_to_previous_step()
        self._replace_containers(lang, readjustment)

    def status(self):
        lintersArray = []
        for linter in self.linters:
            with self.health_check_mutex:
                health_check_result = self.health_check_info.get(linter.container.address)

            if health_check_result is None:
                continue
            
            linterDict = {}
            linterDict[linter.container.address] = dict(
                version=linter.version,
                lang=linter.lang,
                request_count=health_check_result["request_count"],
                is_healthy=health_check_result["is_healthy"]
            )
            lintersArray.append(linterDict)

        return lintersArray
