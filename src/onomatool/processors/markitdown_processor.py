import glob
import os
import subprocess
import tempfile
from typing import Any

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
    """Unified processor for multiple formats using markitdown library"""

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

    def process(self, file_path: str) -> Any | None:
        """
        Process a file using markitdown library. For PDFs, also generate images for each page.
        For PPTX, generate images for each slide. For SVG, render to PNG.
        Returns a dict with 'markdown', 'images', and 'tempdir' (if images are generated).
        """
        try:
            ext = os.path.splitext(file_path)[1].lower()
            result = self.md.convert(file_path)
            if ext == ".pdf" and fitz is not None:
                images = []
                tempdir = tempfile.TemporaryDirectory()
                if self.debug:
                    print(f"[DEBUG] Created tempdir for PDF: {tempdir.name}")
                doc = fitz.open(file_path)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap()
                    img_path = os.path.join(tempdir.name, f"page_{page_num + 1}.png")
                    pix.save(img_path)
                    images.append(img_path)
                    if self.debug:
                        print(f"[DEBUG] Created image: {img_path}")
                return {
                    "markdown": result.text_content,
                    "images": images,
                    "tempdir": tempdir,
                }
            elif ext == ".pptx":
                images = []
                tempdir = tempfile.TemporaryDirectory()
                if self.debug:
                    print(f"[DEBUG] Created tempdir for PPTX: {tempdir.name}")
                    print(f"[DEBUG] Processing file: {file_path}")
                try:
                    # Step 1: Convert PPTX to PDF
                    basename = os.path.splitext(os.path.basename(file_path))[0]
                    pdf_path = os.path.join(tempdir.name, f"{basename}.pdf")
                    soffice_cmd = [
                        "soffice",
                        "--headless",
                        "--convert-to",
                        "pdf",
                        file_path,
                        "--outdir",
                        tempdir.name,
                    ]
                    result = subprocess.run(soffice_cmd, capture_output=True, text=True)
                    if result.returncode != 0 or not os.path.exists(pdf_path):
                        print(f"[PPTX2IMG ERROR] soffice failed: {result.stderr}")
                        return None
                    if self.debug:
                        print(f"[DEBUG] Created PDF: {pdf_path}")
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
                    result = subprocess.run(convert_cmd, capture_output=True, text=True)
                    if result.returncode != 0:
                        print(f"[PPTX2IMG ERROR] convert failed: {result.stderr}")
                        return None
                    # Step 3: Collect images
                    jpeg_files = sorted(
                        glob.glob(os.path.join(tempdir.name, f"{basename}-*.jpeg"))
                    )
                    if self.debug:
                        for img_path in jpeg_files:
                            print(f"[DEBUG] Created image: {img_path}")
                    if not jpeg_files:
                        print("[PPTX2IMG ERROR] No images generated from PPTX.")
                        return None
                    images.extend(jpeg_files)
                    return {
                        "markdown": result.text_content,
                        "images": images,
                        "tempdir": tempdir,
                    }
                except Exception as e:
                    print(f"[PPTX2IMG ERROR] {e}")
                    return None
            elif ext == ".svg":
                # No conversion here; handled elsewhere
                return result.text_content
            else:
                return result.text_content
        except Exception as e:
            print(f"Error processing {file_path} with Markitdown: {e}")
            return None
