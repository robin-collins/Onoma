import os
import tempfile
from pathlib import Path

import chardet


class TextProcessor:
    """Processor for text files (.txt, .md, .note, etc.)"""

    def __init__(self):
        self.temp_files_created = []

    def detect_encoding(self, file_path: str) -> str:
        """
        Detect the encoding of a file using chardet.

        Args:
            file_path: Path to the file

        Returns:
            Detected encoding as string
        """
        with open(file_path, "rb") as file:
            raw_data = file.read()

        result = chardet.detect(raw_data)
        encoding = result["encoding"]
        confidence = result["confidence"]

        # Handle common encoding issues
        if encoding and encoding.lower() == "windows-1252" and confidence < 0.9:
            # Often misdetected UTF-8
            encoding = "utf-8"
        elif not encoding or confidence < 0.7:
            # Low confidence or no detection, default to UTF-8
            encoding = "utf-8"

        return encoding

    def ensure_utf8_file(self, file_path: str) -> str:
        """
        Ensure file is UTF-8 encoded, create temp copy if needed.

        Args:
            file_path: Path to the original file

        Returns:
            Path to UTF-8 encoded file (original or temp copy)
        """
        encoding = self.detect_encoding(file_path)

        # Normalize encodings that are UTF-8 compatible
        normalized_encoding = encoding.lower() if encoding else "utf-8"
        if normalized_encoding in ["utf-8", "ascii", "utf-8-sig"]:
            return file_path

        # Create temporary UTF-8 copy
        temp_file = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=Path(file_path).suffix, delete=False
        )

        try:
            with open(file_path, encoding=encoding) as original:
                temp_file.write(original.read())
            temp_file.close()

            self.temp_files_created.append(temp_file.name)
            return temp_file.name

        except Exception as e:
            temp_file.close()
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            raise Exception(f"Failed to create UTF-8 copy: {e}") from e

    def cleanup_temp_encoding_file(
        self, original_path: str, temp_path: str | None = None
    ):
        """
        Clean up temporary encoding files.

        Args:
            original_path: Path to the original file
            temp_path: Path to the temporary file (optional, for backwards compatibility)
        """
        if temp_path is None:
            # Single parameter mode - assume original_path is the temp file to clean
            temp_file_path = original_path
        else:
            # Two parameter mode - only clean if temp_path differs from original_path
            if temp_path == original_path:
                return  # Don't delete the original file
            temp_file_path = temp_path

        if temp_file_path in self.temp_files_created:
            try:
                os.unlink(temp_file_path)
                self.temp_files_created.remove(temp_file_path)
            except FileNotFoundError:
                pass

    def process(self, file_path: str) -> str | None:
        """
        Read and return the content of a text file with proper encoding handling.

        Args:
            file_path: Path to the text file

        Returns:
            Content of the file as string, or None if file can't be read
        """
        utf8_file_path = None
        try:
            # Ensure the file is UTF-8 encoded
            utf8_file_path = self.ensure_utf8_file(file_path)

            with open(utf8_file_path, encoding="utf-8") as file:
                content = file.read()

            # Clean up temp file if created
            if utf8_file_path != file_path:
                self.cleanup_temp_encoding_file(file_path, utf8_file_path)

            return content

        except Exception:
            # Clean up temp file if created
            if utf8_file_path and utf8_file_path != file_path:
                self.cleanup_temp_encoding_file(file_path, utf8_file_path)
            return None
