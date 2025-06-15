import pytest
from onomatool.processors.text_processor import TextProcessor

def test_process_success(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("hello world", encoding="utf-8")
    tp = TextProcessor()
    assert tp.process(str(f)) == "hello world"

def test_process_file_not_found(tmp_path, monkeypatch):
    tp = TextProcessor()
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    assert tp.process(str(tmp_path / "missing.txt")) is None

def test_process_non_utf8(tmp_path, monkeypatch):
    f = tmp_path / "b.txt"
    # Write bytes that are not valid utf-8
    f.write_bytes(b"\xff\xfe\xfd")
    tp = TextProcessor()
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    assert tp.process(str(f)) is None