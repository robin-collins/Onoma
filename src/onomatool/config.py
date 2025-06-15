import os
from typing import Any

import toml

DEFAULT_CONFIG = {
    "default_provider": "openai",
    "openai_api_key": "",
    "openai_base_url": "https://api.openai.com/v1",
    "google_api_key": "",
    "naming_convention": "snake_case",
    "llm_model": "gpt-4o",
    "min_filename_words": 5,
    "max_filename_words": 15,
    "system_prompt": "",
    "user_prompt": "",
    "image_prompt": "",
    "markitdown": {
        "enable_plugins": False,
        "docintel_endpoint": "",
    },
}


def get_config(config_path: str | None = None) -> dict[str, Any]:
    """
    Load configuration from the given config_path or from ~/.onomarc if not specified.
    Returns the config as a dict, or DEFAULT_CONFIG if loading fails.
    """
    if config_path is None:
        config_path = os.path.expanduser("~/.onomarc")
    else:
        config_path = os.path.expanduser(config_path)
    if os.path.exists(config_path):
        try:
            with open(config_path) as f:
                return toml.load(f)
        except Exception:
            pass
    return DEFAULT_CONFIG
