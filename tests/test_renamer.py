import os
import pytest
from onomatool.renamer import rename_file

def test_rename_file_success(tmp_path, monkeypatch):
    src = tmp_path / "original.txt"
    src.write_text("data")
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    rename_file(str(src), "renamed.txt")
    assert not src.exists()
    assert (tmp_path / "renamed.txt").exists()

def test_rename_file_conflict(tmp_path, monkeypatch):
    src = tmp_path / "original.txt"
    src.write_text("data")
    (tmp_path / "renamed.txt").write_text("other")
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    rename_file(str(src), "renamed.txt")
    assert not src.exists()
    assert (tmp_path / "renamed_2.txt").exists()

def test_rename_file_extension_preserved(tmp_path, monkeypatch):
    src = tmp_path / "original.md"
    src.write_text("data")
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    rename_file(str(src), "renamed.txt")
    # Should preserve .md extension
    assert (tmp_path / "renamed.md").exists()