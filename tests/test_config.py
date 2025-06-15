import os

import toml

from onomatool.config import DEFAULT_CONFIG, get_config


def test_get_config_default(monkeypatch):
    # No config file exists, should return DEFAULT_CONFIG
    monkeypatch.setattr(os.path, "exists", lambda path: False)
    assert get_config("/nonexistent.toml") == DEFAULT_CONFIG


def test_get_config_valid(tmp_path):
    config_data = {"default_provider": "mock", "llm_model": "test-model"}
    config_path = tmp_path / "config.toml"
    config_path.write_text(toml.dumps(config_data))
    loaded = get_config(str(config_path))
    assert loaded["default_provider"] == "mock"
    assert loaded["llm_model"] == "test-model"


def test_get_config_error(monkeypatch, tmp_path):
    # Simulate error in toml.load
    config_path = tmp_path / "bad.toml"
    config_path.write_text("not a valid toml")
    monkeypatch.setattr("toml.load", lambda f: (_ for _ in ()).throw(Exception("fail")))
    # Should fallback to DEFAULT_CONFIG
    assert get_config(str(config_path)) == DEFAULT_CONFIG
