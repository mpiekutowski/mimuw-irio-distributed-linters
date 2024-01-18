from typing import List, Optional
from dataclasses import dataclass
from math import ceil

@dataclass
class Readjustment():
    from_version: str
    to_version: str
    count: int

@dataclass
class UpdateStatus():
    is_updating: bool
    current_version: str
    next_version: Optional[str]
    progress: Optional[float]

class VersionTracker():
    def __init__(self, initial_version: str, update_steps: List[float]):
        if len(update_steps) == 0:
            raise ValueError('At least one update step is required')
        
        if update_steps[-1] != 100:
            raise ValueError('Last update step must be 100')

        self._update_steps: List[int] = update_steps
            
        self._current_version: str = initial_version
        self._is_updating: bool = False
        self._count: int = 0
        self._current_version_count: int = 0

        # These are not None only when updating
        self._next_version: Optional[str] = None
        self._update_step_index: Optional[int] = None
        self._next_version_count: Optional[int] = None


    def _calculate_readjustment(self) -> Optional[Readjustment]:
        # There's nothing to readjust if there is just one version
        if self._is_updating is False:
            return None

        step = self._update_steps[self._update_step_index]

        target_next_version_count = ceil(self._count * step / 100.)
        target_current_version_count = self._count - target_next_version_count

        if step != 100 and self._count > 1 and target_current_version_count == 0:
            # During partial update there should be at least one current version, 
            # even if the ratio is not ideal
            target_current_version_count = 1
            target_next_version_count -= 1

        if self._current_version_count > target_current_version_count:
            # Too much current version, readjust from current to next
            return Readjustment(
                from_version=self._current_version,
                to_version=self._next_version,
                count=self._current_version_count - target_current_version_count
            )
        
        if self._next_version_count > target_next_version_count:
            # Too much next version, readjust from next to current
            return Readjustment(
                from_version=self._next_version,
                to_version=self._current_version,
                count=self._next_version_count - target_next_version_count
            )
        
        return None


    def determine_version(self) -> str:
        if not self._is_updating:
            return self._current_version
        
        # Check if adding current version would not require readjustment
        # QUESTION: This is a bit of a hack, is there a better way to do this?
        # Also, not thread safe
        self._count += 1
        self._current_version_count += 1
        readjustment = self._calculate_readjustment()
        self._count -= 1
        self._current_version_count -= 1

        if readjustment is None:
            return self._current_version
        else:
            return self._next_version


    def add(self, version: str) -> Optional[Readjustment]:
        if version == self._current_version:
            self._current_version_count += 1
        elif version == self._next_version:
            self._next_version_count += 1
        else:
            raise ValueError(f'Version {version} is not allowed')
        self._count += 1

        return self._calculate_readjustment()


    def remove(self, version: str) -> Optional[Readjustment]:
        if version == self._current_version:
            if self._current_version_count == 0:
                raise ValueError(f'Version {version} is not allowed - count is 0')
            
            self._current_version_count -= 1
        elif version == self._next_version:
            if self._next_version_count == 0:
                raise ValueError(f'Version {version} is not allowed - count is 0')
            
            self._next_version_count -= 1
        else:
            raise ValueError(f'Version {version} is not allowed')
        self._count -= 1

        return self._calculate_readjustment()


    def start_update(self, version: str) -> Optional[Readjustment]:
        if self._is_updating:
            raise ValueError('Cannot start update, already updating')
        
        self._is_updating = True
        self._update_step_index = 0
        self._next_version = version
        self._next_version_count = 0

        return self._calculate_readjustment()

    def move_to_next_step(self) -> Optional[Readjustment]:
        if not self._is_updating:
            raise ValueError('Cannot move to next step, not updating')
        
        if self._update_step_index + 1 == len(self._update_steps):
            raise ValueError('Cannot move to next step, already at last step')
        
        self._update_step_index += 1

        return self._calculate_readjustment()
        


    def move_to_previous_step(self) -> Optional[Readjustment]:
        if not self._is_updating:
            raise ValueError('Cannot move to previous step, not updating')
        
        if self._update_step_index - 1 < 0:
            raise ValueError('Cannot move to previous step, already at first step')
        
        self._update_step_index -= 1

        return self._calculate_readjustment()

    def finish_update(self):
        if not self._is_updating:
            raise ValueError('Cannot finish update, not updating')
        
        if self._update_step_index + 1 != len(self._update_steps):
            raise ValueError('Cannot finish update, not at last step')
        
        self._is_updating = False
        self._current_version = self._next_version
        self._current_version_count = self._next_version_count
        self._next_version = None
        self._update_step_index = None
        self._next_version_count = None


    def update_status(self) -> UpdateStatus:
        return UpdateStatus(
            is_updating=self._is_updating,
            current_version=self._current_version,
            next_version=self._next_version,
            progress=self._update_steps[self._update_step_index] if self._is_updating else None
        )
    
    