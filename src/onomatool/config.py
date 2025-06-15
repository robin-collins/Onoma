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
    "system_prompt": "",
    "user_prompt": "",
    "image_prompt": "",
    "markitdown": {
        "enable_plugins": False,
        "docintel_endpoint": "",
    },
}


def get_config() -> dict[str, Any]:
    """Load configuration from ~/.onomarc or return defaults"""
    config_path = os.path.expanduser("~/.onomarc")
    if os.path.exists(config_path):
        try:
            with open(config_path) as f:
                return toml.load(f)
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults")
    return DEFAULT_CONFIG
