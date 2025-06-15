import os
import pytest
from onomatool.file_collector import collect_files

def test_collect_files_basic(tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("1")
    f2.write_text("2")
    files = collect_files(str(tmp_path / "*.txt"))
    assert set(map(os.path.basename, files)) == {"a.txt", "b.txt"}

def test_collect_files_recursive(tmp_path):
    sub = tmp_path / "subdir"
    sub.mkdir()
    (sub / "c.txt").write_text("3")
    files = collect_files(str(tmp_path / "**/*.txt"))
    assert any("c.txt" in f for f in files)

def test_collect_files_no_match(tmp_path):
    files = collect_files(str(tmp_path / "*.nomatch"))
    assert files == []