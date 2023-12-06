import tomllib

# TODO: make it so this module can be imported from anywhere and still read this correctly
with open("../config/config.toml", "rb") as f:
    CONFIG = tomllib.load(f)

with open("../config/secret.toml", "rb") as f:
    SECRET = tomllib.load(f)
