from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin
from yamldataclassconfig.config import YamlDataClassConfig


@dataclass
class Postprocessing(DataClassJsonMixin):
    min_gap_to_connect: int = None
    mode: str = None


@dataclass
class Scenes_filtration(DataClassJsonMixin):
    label: int = None
    start: int = None
    end: int = None


@dataclass
class Config(YamlDataClassConfig):
    postprocessing: Postprocessing = None
    scenes_filtration: Scenes_filtration = None


if __name__ == '__main__':
    config = Config()
    config.load()
