import glob
import os
import subprocess
import tempfile
from typing import Any

import chardet
from markitdown import MarkItDown

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None
try:
    from PIL import Image, ImageDraw
    from pptx import Presentation
except ImportError:
    Presentation = None
    Image = None
    ImageDraw = None
try:
    import cairosvg
except ImportError:
    cairosvg = None
try:
    import requests
except ImportError:
    requests = None


class MarkitdownProcessor:
    """Unified processor for multiple formats using markitdown library with UTF-8 encoding support"""

    def __init__(self, config: dict, debug: bool = False):
        """
        Initialize the Markitdown processor with configuration

        Args:
            config: Configuration dictionary with markitdown settings
            debug: If True, print tempdir and image paths for PDF/PPTX processing
        """
        self.config = config
        self.debug = debug
        self.md = MarkItDown(
            enable_plugins=config.get("enable_plugins", False),
            docintel_endpoint=config.get("docintel_endpoint", ""),
            llm_model=config.get("llm_model", "gpt-4o"),
        )

    def detect_encoding(self, file_path: str) -> str:
        """
        Detect the encoding of a text file using chardet

        Args:
            file_path: Path to the file to analyze

        Returns:
            Detected encoding string (defaults to 'utf-8' if detection fails)
        """
        try:
            with open(file_path, "rb") as f:
                # Read a sample of the file for encoding detection
                raw_data = f.read(10240)  # Read first 10KB
                if not raw_data:
                    return "utf-8"

                result = chardet.detect(raw_data)
                encoding = result.get("encoding", "utf-8")
                confidence = result.get("confidence", 0)

                if self.debug:
                    pass

                # Handle special cases where chardet misidentifies UTF-8 as Windows-1252
                # This happens when files contain em dashes, smart quotes, etc.
                if encoding and encoding.lower() == "windows-1252":
                    try:
                        # Try to decode as UTF-8 first
                        raw_data.decode("utf-8")
                        if self.debug:
                            pass
                        return "utf-8"
                    except UnicodeDecodeError:
                        # If UTF-8 fails, stick with Windows-1252
                        pass

                # Fall back to utf-8 for low confidence or None encoding
                if not encoding or confidence < 0.7:
                    if self.debug:
                        pass
                    return "utf-8"

                return encoding

        except Exception:
            if self.debug:
                pass
            return "utf-8"

    def ensure_utf8_file(self, file_path: str) -> str:
        """
        Ensure a file is UTF-8 encoded by creating a temporary UTF-8 copy if needed

        Args:
            file_path: Path to the original file

        Returns:
            Path to UTF-8 encoded file (original if already UTF-8, temp file otherwise)
        """
        # Only handle text-like files that might have encoding issues
        ext = os.path.splitext(file_path)[1].lower()
        text_extensions = {
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
        }

        if ext not in text_extensions:
            return file_path

        detected_encoding = self.detect_encoding(file_path)

        # Force UTF-8 conversion for all text files to ensure MarkItDown compatibility
        # Even files detected as UTF-8 may have BOM or other issues that confuse MarkItDown
        if detected_encoding.lower() in ("utf-8", "utf8"):
            # For UTF-8 files, try reading them first to ensure they're valid
            try:
                with open(file_path, encoding="utf-8") as test_file:
                    test_file.read(1024)  # Test read first 1KB
                # If successful and no debug mode, we can return original
                if not self.debug:
                    return file_path
            except UnicodeDecodeError:
                # File claims to be UTF-8 but isn't, treat as non-UTF-8
                if self.debug:
                    pass
        elif detected_encoding.lower() == "ascii":
            # ASCII is UTF-8 compatible, but let's be safe for MarkItDown
            if not self.debug:
                return file_path

        # Create temporary UTF-8 file
        try:
            temp_fd, temp_path = tempfile.mkstemp(suffix=ext, prefix="onoma_utf8_")

            with (
                open(file_path, encoding=detected_encoding, errors="replace") as source,
                os.fdopen(temp_fd, "w", encoding="utf-8") as target,
            ):
                target.write(source.read())

            if self.debug:
                pass

            return temp_path

        except Exception:
            if self.debug:
                pass
            # Clean up temp file if it was created
            try:
                if "temp_path" in locals():
                    os.unlink(temp_path)
            except (OSError, FileNotFoundError):
                pass
            return file_path

    def cleanup_temp_encoding_file(self, original_path: str, temp_path: str):
        """
        Clean up temporary UTF-8 file if it's different from original

        Args:
            original_path: Path to original file
            temp_path: Path to temporary file (may be same as original)
        """
        if temp_path != original_path:
            try:
                os.unlink(temp_path)
                if self.debug:
                    pass
            except Exception:
                if self.debug:
                    pass

    def process(self, file_path: str) -> Any | None:
        """
        Process a file using markitdown library with proper UTF-8 encoding handling.
        For PDFs, also generate images for each page.
        For PPTX, generate images for each slide. For SVG, render to PNG.
        Returns a dict with 'markdown', 'images', and 'tempdir' (if images are generated).
        """
        utf8_file_path = None
        try:
            # Ensure UTF-8 encoding for text files
            utf8_file_path = self.ensure_utf8_file(file_path)
            ext = os.path.splitext(file_path)[1].lower()

            # Try to process with MarkItDown
            result = None
            try:
                result = self.md.convert(utf8_file_path)
            except Exception as conversion_error:
                # Check if this is a Unicode-related error and if it's a text file
                error_str = str(conversion_error)
                is_unicode_error = (
                    "UnicodeDecodeError" in error_str or "ascii" in error_str.lower()
                )
                is_text_file = ext in {
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
                }

                if is_unicode_error and is_text_file:
                    # MarkItDown has encoding issues, use direct text processing
                    if self.debug:
                        pass

                    try:
                        # Read the file directly with UTF-8 handling
                        with open(
                            utf8_file_path, encoding="utf-8", errors="replace"
                        ) as f:
                            content = f.read()

                        # Create a mock result object similar to MarkItDown's output
                        class MockResult:
                            def __init__(self, text):
                                self.text_content = text

                        result = MockResult(content)
                        if self.debug:
                            pass

                    except Exception:
                        if self.debug:
                            pass
                        raise conversion_error from None
                else:
                    # Not a Unicode error or not a text file, re-raise the original error
                    raise

            # If we reach here, we have a successful result
            if ext == ".pdf" and fitz is not None:
                images = []
                if self.debug:
                    # Create a regular temp directory that won't auto-cleanup
                    tempdir_path = tempfile.mkdtemp(prefix="onoma_pdf_")
                    tempdir = type(
                        "TempDir", (), {"name": tempdir_path, "cleanup": lambda: None}
                    )()
                else:
                    tempdir = tempfile.TemporaryDirectory()
                doc = fitz.open(
                    file_path
                )  # Use original file for binary PDF processing
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap()
                    img_path = os.path.join(tempdir.name, f"page_{page_num + 1}.png")
                    pix.save(img_path)
                    images.append(img_path)

                # Save markdown content to file in debug mode
                if self.debug:
                    markdown_path = os.path.join(tempdir.name, "extracted_content.md")
                    with open(markdown_path, "w", encoding="utf-8") as f:
                        f.write(result.text_content)

                return {
                    "markdown": result.text_content,
                    "images": images,
                    "tempdir": tempdir,
                }
            if ext == ".pptx":
                images = []
                if self.debug:
                    # Create a regular temp directory that won't auto-cleanup
                    tempdir_path = tempfile.mkdtemp(prefix="onoma_pptx_")
                    tempdir = type(
                        "TempDir", (), {"name": tempdir_path, "cleanup": lambda: None}
                    )()
                else:
                    tempdir = tempfile.TemporaryDirectory()
                try:
                    # Step 1: Convert PPTX to PDF (use original file for binary processing)
                    basename = os.path.splitext(os.path.basename(file_path))[0]
                    pdf_path = os.path.join(tempdir.name, f"{basename}.pdf")
                    soffice_cmd = [
                        "soffice",
                        "--headless",
                        "--convert-to",
                        "pdf",
                        file_path,  # Use original file
                        "--outdir",
                        tempdir.name,
                    ]
                    soffice_result = subprocess.run(
                        soffice_cmd, capture_output=True, text=True
                    )
                    if soffice_result.returncode != 0 or not os.path.exists(pdf_path):
                        return None
                    # Step 2: Convert PDF to JPEGs
                    output_pattern = os.path.join(tempdir.name, f"{basename}-%d.jpeg")
                    convert_cmd = [
                        "convert",
                        "-adaptive-resize",
                        "x1024",
                        "-density",
                        "150",
                        pdf_path,
                        "-quality",
                        "80",
                        output_pattern,
                    ]
                    convert_result = subprocess.run(
                        convert_cmd, capture_output=True, text=True
                    )
                    if convert_result.returncode != 0:
                        return None
                    # Step 3: Collect images
                    jpeg_files = sorted(
                        glob.glob(os.path.join(tempdir.name, f"{basename}-*.jpeg"))
                    )
                    if not jpeg_files:
                        return None
                    images.extend(jpeg_files)

                    # Save markdown content to file in debug mode
                    if self.debug:
                        markdown_path = os.path.join(
                            tempdir.name, "extracted_content.md"
                        )
                        with open(markdown_path, "w", encoding="utf-8") as f:
                            f.write(result.text_content)

                    return {
                        "markdown": result.text_content,
                        "images": images,
                        "tempdir": tempdir,
                    }
                except Exception:
                    return None
            elif ext == ".svg":
                # No conversion here; handled elsewhere
                # But save markdown content in debug mode
                if self.debug and result.text_content:
                    tempdir_path = tempfile.mkdtemp(prefix="onoma_svg_md_")
                    tempdir = type(
                        "TempDir", (), {"name": tempdir_path, "cleanup": lambda: None}
                    )()
                    markdown_path = os.path.join(tempdir.name, "extracted_content.md")
                    with open(markdown_path, "w", encoding="utf-8") as f:
                        f.write(result.text_content)
                    return {
                        "markdown": result.text_content,
                        "tempdir": tempdir,
                    }
                return result.text_content
            else:
                # For all other file types (docx, txt, etc.), save markdown in debug mode
                if self.debug and result.text_content:
                    file_ext = ext.lstrip(".")
                    tempdir_path = tempfile.mkdtemp(prefix=f"onoma_{file_ext}_")
                    tempdir = type(
                        "TempDir", (), {"name": tempdir_path, "cleanup": lambda: None}
                    )()
                    markdown_path = os.path.join(tempdir.name, "extracted_content.md")
                    with open(markdown_path, "w", encoding="utf-8") as f:
                        f.write(result.text_content)
                    return {
                        "markdown": result.text_content,
                        "tempdir": tempdir,
                    }
                return result.text_content

        except UnicodeDecodeError:
            return None
        except Exception:
            return None
        finally:
            # Clean up temporary UTF-8 file if created
            if utf8_file_path:
                self.cleanup_temp_encoding_file(file_path, utf8_file_path)
