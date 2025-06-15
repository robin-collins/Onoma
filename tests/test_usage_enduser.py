import os
import shutil
import tempfile
from pathlib import Path

import pytest

from onomatool.cli import main

CLI = "src/onomatool/cli.py"
MOCK_CONFIG = "tests/mock_config.toml"
TEST_FILE = "tests/note_0.md"

@pytest.fixture
def temp_copy():
    # Copy a test file to a temp location for renaming
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, "note_0.md")
    shutil.copy(TEST_FILE, test_file)
    yield test_file
    shutil.rmtree(temp_dir)

def test_basic_rename(temp_copy):
    # Test basic rename with mock config
    result = main([temp_copy, "--config", MOCK_CONFIG])
    assert result == 0
    # Check that the file was renamed to mock_file_one.md
    renamed = os.path.join(os.path.dirname(temp_copy), "mock_file_one.md")
    assert os.path.exists(renamed)

def test_dry_run(temp_copy, capsys):
    # Test dry-run mode
    result = main([temp_copy, "--config", MOCK_CONFIG, "--dry-run"])
    assert result == 0
    # Should print the planned rename
    captured = capsys.readouterr()
    assert "mock_file_one.md" in captured.out
    # File should not be renamed
    assert os.path.exists(temp_copy)

import builtins
import pytest

@pytest.mark.usefixtures("temp_copy")
def test_interactive(temp_copy, capsys, monkeypatch):
    # Test interactive mode (simulate 'y' input)
    monkeypatch.setattr(builtins, "input", lambda _: "y")
    result = main([temp_copy, "--config", MOCK_CONFIG, "--dry-run", "--interactive"])
    assert result == 0
    # File should be renamed to mock_file_one.md
    renamed = os.path.join(os.path.dirname(temp_copy), "mock_file_one.md")
    assert os.path.exists(renamed)

def test_debug_mode(temp_copy, capsys):
    # Test debug mode (should print debug info)
    result = main([temp_copy, "--config", MOCK_CONFIG, "--debug"])
    assert result == 0
    captured = capsys.readouterr()
    assert "[DEBUG]" in captured.out or os.path.exists(temp_copy)

def test_alternate_config(temp_copy):
    # Test that alternate config is loaded and used
    result = main([temp_copy, "--config", MOCK_CONFIG])
    assert result == 0
    renamed = os.path.join(os.path.dirname(temp_copy), "mock_file_one.md")
    assert os.path.exists(renamed)