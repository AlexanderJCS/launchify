import tomllib


def load_toml(filepath: str):
    with open(filepath, "rb") as f:
        return tomllib.load(f)
