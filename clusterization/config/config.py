from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin
from yamldataclassconfig.config import YamlDataClassConfig


@dataclass
class Dbscan(DataClassJsonMixin):
    eps: int = None
    samples: int = None


@dataclass
class Config(YamlDataClassConfig):
    dbscan: Dbscan = None


if __name__ == '__main__':
    config = Config()
    config.load()
