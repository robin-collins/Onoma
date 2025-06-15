from unittest.mock import MagicMock

from onomatool.file_dispatcher import FileDispatcher


def test_get_processor_md_txt(monkeypatch):
    config = {}
    dispatcher = FileDispatcher(config)
    assert dispatcher.get_processor("file.md").__class__.__name__ == "TextProcessor"
    assert dispatcher.get_processor("file.txt").__class__.__name__ == "TextProcessor"


def test_get_processor_other(monkeypatch):
    config = {}
    dispatcher = FileDispatcher(config)
    # Should return MarkitdownProcessor for .pdf
    assert (
        dispatcher.get_processor("file.pdf").__class__.__name__ == "MarkitdownProcessor"
    )


def test_process_calls_correct(monkeypatch):
    config = {}
    dispatcher = FileDispatcher(config)
    # Patch processors
    dispatcher.processors[".md"] = MagicMock()
    dispatcher.processors[".md"].process.return_value = "ok"
    assert dispatcher.process("file.md") == "ok"
    # Patch markitdown_processor
    dispatcher.markitdown_processor = MagicMock()
    dispatcher.markitdown_processor.process.return_value = "markitdown"
    assert dispatcher.process("file.pdf") == "markitdown"
