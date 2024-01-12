import tomllib
import json


def load_toml(filepath: str):
    with open(filepath, "rb") as f:
        return tomllib.load(f)


def load_json(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)


def write_json(filepath: str, data: dict):
    with open(filepath, "w") as f:
        json.dump(data, f)
