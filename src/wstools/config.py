import json
import logging
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)
_config_cache: dict[str, Any] | None = None


class ConfigError(Exception):
    """Configuration file could not be loaded or validated."""


def load_config(path: str = "config.json") -> dict[str, Any]:
    global _config_cache
    if _config_cache is not None:
        return _config_cache

    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"Configuration file not found: {config_path}")

    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Error decoding JSON from {config_path}: {exc}") from exc
    except OSError as exc:
        raise ConfigError(f"Error reading configuration file {config_path}: {exc}") from exc

    required_keys = ["DISCORD_TOKEN", "GUILDS"]
    for key in required_keys:
        if key not in data:
            raise ConfigError(f"Missing required key '{key}' in {config_path}")

    if not isinstance(data["GUILDS"], list) or not all(
        isinstance(guild_id, int) for guild_id in data["GUILDS"]
    ):
        raise ConfigError("GUILDS must be a list of Discord guild IDs.")

    exempt_users = data.get("RATE_LIMIT_EXEMPT_USER_IDS", [])
    if not isinstance(exempt_users, list) or not all(
        isinstance(user_id, int) for user_id in exempt_users
    ):
        raise ConfigError("RATE_LIMIT_EXEMPT_USER_IDS must be a list of Discord user IDs.")

    _config_cache = data
    _log.info("Configuration loaded successfully from %s", config_path)
    return _config_cache


def get_config() -> dict[str, Any]:
    if _config_cache is None:
        load_config()

    if _config_cache is None:
        raise ConfigError("Configuration is not available.")

    return _config_cache
