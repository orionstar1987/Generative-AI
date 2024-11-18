from dataclasses import dataclass
from typing import Sequence
import os

@dataclass
class IndexConfig:
    CommonFiles: list[str]
    keys: Sequence[str] = tuple(['CommonFiles'])
    mode: str = 'local' # 'local' or 'azure'
    root_dir: str = f'{os.getenv("ROOT_DIR", ".")}/backend/files'

    def load(self, key: str):
        """
        load data to target directory and return path
        """
        if key not in self.keys:
            raise KeyError(f'Key {key} not found')
        if self.mode == 'azure':
            # TODO: load file from Azure
            ...
            return
        if self.mode == 'local':
            return f'{self.root_dir}/{key}'



local_index_config = IndexConfig(CommonFiles=['2020 Expectation Guide.pdf', 'Benefits Guide.pdf'])

property_to_idx = {
    'WCA': ['us', 'all'],
    'WCM': ['us', 'all'],
    'WCW': ['us', 'all'],
    'WCI': ['us', 'all'],
    'WCH': ['us', 'all'],
    'WCHA': ['car', 'car-en', 'all'],
    'WCHC': ['car', 'car-en', 'all'],
    'WCMC': ['esp', 'esp-en', 'all'],
    'WCB': ['ch', 'ch-en', 'all']
}