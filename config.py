import json
from pathlib import Path

class ConfigError(Exception):
    pass

def save_config(path, config):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def load_config(path, defaults):
    result = dict(defaults)
    try:
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        return result
    except json.decoder.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in {path}: {e}") from e
    if not isinstance(config, dict):
        raise ConfigError(f"Config must be a JSON object, got {type(config).__name__}")
    result.update(config)
    return result

if __name__ == "__main__":
    Path("settings.json").unlink(missing_ok=True)
    DEFAULTS = {"theme": "light", "font_size": 14, "language": "uk"}
    print(load_config("settings.json", DEFAULTS))
    save_config("settings.json", {"theme": "dark", "font_size": 16})
    print(load_config("settings.json", DEFAULTS))
    print(DEFAULTS)
    Path("bad.json").write_text("{theme: dark}", encoding="utf-8")

    try:
        load_config("bad.json", DEFAULTS)
    except ConfigError as e:
        print(f"ConfigError: {e} | cause: {type(e.__cause__).__name__}")

    Path("list.json").write_text("[1, 2]", encoding="utf-8")
    try:
        load_config("list.json", DEFAULTS)
    except ConfigError as e:
        print(f"ConfigError: {e} | cause: {type(e.__cause__).__name__}")