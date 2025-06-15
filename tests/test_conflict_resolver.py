import pytest
from onomatool.conflict_resolver import resolve_conflict

def test_no_conflict():
    assert resolve_conflict("file.txt", ["other.txt"]) == "file.txt"

def test_single_conflict():
    assert resolve_conflict("file.txt", ["file.txt"]) == "file_2.txt"

def test_multiple_conflicts():
    existing = ["file.txt", "file_2.txt", "file_3.txt"]
    assert resolve_conflict("file.txt", existing) == "file_4.txt"

def test_conflict_with_number_suffix():
    existing = ["file.txt", "file_2.txt", "file_3.txt", "file_4.txt"]
    assert resolve_conflict("file.txt", existing) == "file_5.txt"