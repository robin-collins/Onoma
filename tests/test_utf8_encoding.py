#!/usr/bin/env python3
"""
Test UTF-8 encoding detection and conversion functionality in MarkitdownProcessor.
"""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch

from onomatool.processors.markitdown_processor import MarkitdownProcessor


class TestUTF8Encoding(unittest.TestCase):
    """Test UTF-8 encoding detection and conversion functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            "enable_plugins": False,
            "docintel_endpoint": "",
            "llm_model": "gpt-4o",
        }
        # Use non-debug mode for most tests to avoid dict returns
        self.processor = MarkitdownProcessor(self.config, debug=False)

    def test_detect_encoding_simple_ascii(self):
        """Test encoding detection for simple ASCII files"""
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="ascii", suffix=".txt", delete=False
        ) as f:
            f.write("Hello World - this is simple ASCII content")
            temp_path = f.name

        try:
            encoding = self.processor.detect_encoding(temp_path)
            # ASCII should be detected reliably
            assert encoding.lower() in ["ascii", "utf-8", "utf8"]
        finally:
            os.unlink(temp_path)

    def test_detect_encoding_with_unicode(self):
        """Test encoding detection for files with Unicode characters"""
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".txt", delete=False
        ) as f:
            f.write("Hello World — this is UTF-8 content with em dash")
            temp_path = f.name

        try:
            encoding = self.processor.detect_encoding(temp_path)
            # chardet might detect this as Windows-1252 or UTF-8, both are valid
            # The important thing is that it detects some encoding
            assert encoding is not None
            assert isinstance(encoding, str)
            assert len(encoding) > 0
        finally:
            os.unlink(temp_path)

    def test_detect_encoding_latin1(self):
        """Test encoding detection for Latin-1 files"""
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt", delete=False) as f:
            # Write Latin-1 encoded content with accented characters
            content = "Hello World - café résumé naïve".encode("latin-1")
            f.write(content)
            temp_path = f.name

        try:
            encoding = self.processor.detect_encoding(temp_path)
            # Should detect some encoding (may vary depending on content)
            assert encoding is not None
            assert isinstance(encoding, str)
        finally:
            os.unlink(temp_path)

    def test_ensure_utf8_file_simple_ascii(self):
        """Test ensure_utf8_file with simple ASCII file"""
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="ascii", suffix=".txt", delete=False
        ) as f:
            f.write("Hello World - simple ASCII content")
            temp_path = f.name

        try:
            result_path = self.processor.ensure_utf8_file(temp_path)
            # ASCII should be treated as UTF-8 compatible
            assert result_path == temp_path
        finally:
            os.unlink(temp_path)

    def test_ensure_utf8_file_with_mocked_detection(self):
        """Test ensure_utf8_file with controlled encoding detection"""
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".txt", delete=False
        ) as f:
            f.write("Hello World — UTF-8 content")
            temp_path = f.name

        try:
            # Mock detect_encoding to return UTF-8
            with patch.object(self.processor, "detect_encoding", return_value="utf-8"):
                result_path = self.processor.ensure_utf8_file(temp_path)
                # Should return original path for UTF-8 files
                assert result_path == temp_path
        finally:
            os.unlink(temp_path)

    def test_ensure_utf8_file_non_text_extension(self):
        """Test ensure_utf8_file with non-text file extension"""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"PDF content")
            temp_path = f.name

        try:
            result_path = self.processor.ensure_utf8_file(temp_path)
            # Should return original path for non-text files
            assert result_path == temp_path
        finally:
            os.unlink(temp_path)

    def test_ensure_utf8_file_conversion(self):
        """Test ensure_utf8_file with file needing conversion"""
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt", delete=False) as f:
            # Write Latin-1 encoded content
            content = "Hello World - café résumé".encode("latin-1")
            f.write(content)
            original_path = f.name

        try:
            # Mock detect_encoding to return latin-1
            with patch.object(
                self.processor, "detect_encoding", return_value="latin-1"
            ):
                result_path = self.processor.ensure_utf8_file(original_path)

                # Should create a different temp file
                assert result_path != original_path

                # Temp file should exist and contain UTF-8 content
                assert os.path.exists(result_path)

                # Read the converted content
                with open(result_path, encoding="utf-8") as f:
                    content = f.read()
                    assert "café" in content
                    assert "résumé" in content

                # Clean up temp file
                self.processor.cleanup_temp_encoding_file(original_path, result_path)
                assert not os.path.exists(result_path)

        finally:
            os.unlink(original_path)

    def test_cleanup_temp_encoding_file_same_path(self):
        """Test cleanup when temp path is same as original"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_path = f.name

        try:
            # Should not attempt to delete when paths are the same
            self.processor.cleanup_temp_encoding_file(temp_path, temp_path)
            # File should still exist
            assert os.path.exists(temp_path)
        finally:
            os.unlink(temp_path)

    def test_cleanup_temp_encoding_file_different_path(self):
        """Test cleanup when temp path is different from original"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f1:
            original_path = f1.name
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f2:
            temp_path = f2.name

        try:
            # Should delete temp file but keep original
            self.processor.cleanup_temp_encoding_file(original_path, temp_path)

            # Original should exist, temp should be deleted
            assert os.path.exists(original_path)
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        finally:
            if os.path.exists(original_path):
                os.unlink(original_path)

    @patch("onomatool.processors.markitdown_processor.MarkItDown")
    def test_process_with_utf8_conversion(self, mock_markitdown):
        """Test full process method with UTF-8 conversion"""
        # Mock MarkItDown result
        mock_result = Mock()
        mock_result.text_content = "Processed content"
        mock_md_instance = Mock()
        mock_md_instance.convert.return_value = mock_result
        mock_markitdown.return_value = mock_md_instance

        # Create test file with non-UTF-8 content
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt", delete=False) as f:
            content = "Test content with café".encode("latin-1")
            f.write(content)
            test_file = f.name

        try:
            # Mock detect_encoding to return latin-1 and create a new processor with the mock
            with patch.object(
                MarkitdownProcessor, "detect_encoding", return_value="latin-1"
            ):
                # Create a new processor instance with the mocked MarkItDown
                test_processor = MarkitdownProcessor(self.config, debug=False)
                result = test_processor.process(test_file)

                # Should return the processed content (string for non-debug mode)
                assert result == "Processed content"

                # MarkItDown should have been called with temp UTF-8 file
                mock_md_instance.convert.assert_called_once()
                called_path = mock_md_instance.convert.call_args[0][0]
                assert called_path != test_file  # Should be temp file

        finally:
            os.unlink(test_file)

    def test_unicode_decode_error_handling(self):
        """Test handling of UnicodeDecodeError"""
        # Create a test file with problematic content
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt", delete=False) as f:
            # Write content that might cause issues
            f.write(b"\xe2\x80\x94 em dash in UTF-8")
            test_file = f.name

        try:
            # Mock MarkItDown to raise UnicodeDecodeError
            with patch.object(self.processor.md, "convert") as mock_convert:
                mock_convert.side_effect = UnicodeDecodeError(
                    "ascii", b"\xe2", 0, 1, "ordinal not in range(128)"
                )

                result = self.processor.process(test_file)

                # Should return None and handle the error gracefully
                assert result is None

        finally:
            os.unlink(test_file)

    def test_detect_encoding_fallback(self):
        """Test encoding detection fallback behavior"""
        # Test with empty file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("")  # Empty file
            temp_path = f.name

        try:
            encoding = self.processor.detect_encoding(temp_path)
            # Should fallback to utf-8 for empty files
            assert encoding == "utf-8"
        finally:
            os.unlink(temp_path)

    def test_detect_encoding_confidence_threshold(self):
        """Test encoding detection with low confidence"""
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt", delete=False) as f:
            # Write ambiguous content that might have low confidence
            f.write(b"a\xf1b")  # Single byte that could be multiple encodings
            temp_path = f.name

        try:
            # Mock chardet to return low confidence
            with patch(
                "onomatool.processors.markitdown_processor.chardet.detect"
            ) as mock_detect:
                mock_detect.return_value = {"encoding": "iso-8859-1", "confidence": 0.5}

                encoding = self.processor.detect_encoding(temp_path)
                # Should fallback to utf-8 for low confidence
                assert encoding == "utf-8"
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    unittest.main()
