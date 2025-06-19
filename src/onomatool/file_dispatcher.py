from .processors.markitdown_processor import MarkitdownProcessor
from .processors.text_processor import TextProcessor


class FileDispatcher:
    """Routes files to appropriate processors based on file type"""

    def __init__(self, config: dict, debug: bool = False):
        self.config = config
        self.debug = debug

        # Text file extensions that should be processed directly without MarkItDown
        self.text_extensions = {
            ".txt",
            ".md",
            ".note",
            ".text",
            ".log",
            ".csv",
            ".json",
            ".xml",
            ".html",
            ".htm",
            ".py",
            ".js",
            ".css",
            ".yaml",
            ".yml",
            ".toml",
            ".ini",
            ".cfg",
        }

        self.processors: dict[str, object] = {}
        # Initialize text processor for all text extensions
        text_processor = TextProcessor()
        for ext in self.text_extensions:
            self.processors[ext] = text_processor

        # Initialize markitdown processor for other formats
        self.markitdown_processor = MarkitdownProcessor(
            self.config.get("markitdown", {}), debug=debug
        )

    def get_processor(self, file_path: str) -> object:
        """Get appropriate processor for the given file"""
        # Get file extension
        from pathlib import Path

        file_ext = Path(file_path).suffix.lower()  # '' when no suffix

        # Check if it's a text file
        if file_ext in self.text_extensions:
            return self.processors[file_ext]
        # Use markitdown for all other supported formats
        return self.markitdown_processor

    def process(self, file_path: str):
        """Process a file using the appropriate processor"""
        processor = self.get_processor(file_path)
        return processor.process(file_path)
