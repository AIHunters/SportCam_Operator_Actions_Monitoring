from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin
from yamldataclassconfig.config import YamlDataClassConfig


@dataclass
class Segmentation(DataClassJsonMixin):
    grid_size: int = None
    threshold: int = None


@dataclass
class Config(YamlDataClassConfig):
    segmentation: Segmentation = None


if __name__ == '__main__':
    config = Config()
    config.load()
