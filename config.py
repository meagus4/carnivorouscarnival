from typing import TypedDict
import json


class Config(TypedDict):
    public_channel: int
    private_channel: int
    public_game_interval: int
    cors_origins: list[str]


def load_config() -> Config:
    with open("config.json") as f:
        config = json.load(f)

    if not isinstance(config["public_channel"], int):
        raise ValueError("public_channel must be set to an int in config.json")

    if not isinstance(config["private_channel"], int):
        raise ValueError(
            "private_channel must be set to an int in config.json")

    if not isinstance(config["public_game_interval"], int):
        raise ValueError(
            "public_game_interval must be set to an int (minutes) in config.json")

    if not isinstance(config["cors_origins"], list):
        raise ValueError(
            "cors_origins must be set to a list of strings in config.json")

    return config
