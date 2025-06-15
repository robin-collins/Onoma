from .config import get_config
from .processors.markitdown_processor import MarkitdownProcessor
from .processors.text_processor import TextProcessor


class FileDispatcher:
    """Routes files to appropriate processors based on file type"""

    def __init__(self, config: dict, debug: bool = False):
        self.config = config
        self.debug = debug
        self.processors: dict[str, object] = {
            ".txt": TextProcessor(),
            ".md": TextProcessor(),
        }
        # Initialize markitdown processor for other formats
        self.markitdown_processor = MarkitdownProcessor(
            self.config.get("markitdown", {}), debug=debug
        )

    def get_processor(self, file_path: str) -> object:
        """Get appropriate processor for the given file"""
        if file_path.endswith((".txt", ".md")):
            return self.processors[file_path[file_path.rfind(".") :]]
        else:
            # Use markitdown for all other supported formats
            return self.markitdown_processor

    def process(self, file_path: str):
        """Process a file using the appropriate processor"""
        processor = self.get_processor(file_path)
        return processor.process(file_path)
