class TextProcessor:
    """Processor for text files (.txt, .md)"""

    def process(self, file_path: str) -> str | None:
        """
        Read and return the content of a text file.

        Args:
            file_path: Path to the text file

        Returns:
            Content of the file as string, or None if file can't be read
        """
        try:
            with open(file_path, encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None
