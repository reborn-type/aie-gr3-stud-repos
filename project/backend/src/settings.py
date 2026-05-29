from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


BACKEND_DIR = Path(__file__).resolve().parents[1]
CONFIGS_DIR = BACKEND_DIR / "configs"
DIRECTORIES_CONFIG_PATH = CONFIGS_DIR / "directories.yaml"


@lru_cache
def load_directories_config() -> dict[str, Any]:
    with DIRECTORIES_CONFIG_PATH.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


@lru_cache
def load_yaml_config(config_name: str) -> dict[str, Any]:
    config_path = CONFIGS_DIR / config_name

    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def get_path(name: str) -> Path:
    paths = load_directories_config()["paths"]
    return (BACKEND_DIR / paths[name]).resolve()


def get_env_path() -> Path:
    return get_path("env_file")
