# Onoma Project File Structure

```
.
├── .cursorignore
├── .gitignore
├── ARCHITECTURE.md
├── CHANGELOG.md
├── FILETREE.md
├── images/
└── onomatool/
    ├── __init__.py
    ├── cli.py
    ├── file_collector.py
    ├── processors/
    │   ├── text_processor.py
    │   └── markitdown_processor.py
    ├── conflict_resolver.py
    ├── renamer.py
    └── llm_integration.py
```

## Key Files
- `onomatool/cli.py`: Main entry point for the CLI tool
- `onomatool/file_collector.py`: Collects files using glob patterns
- `onomatool/processors/text_processor.py`: Handles simple text file processing (.txt, .md)
- `onomatool/processors/markitdown_processor.py`: Handles complex file processing (PDF, DOCX, images, etc.) via Markitdown
- `onomatool/conflict_resolver.py`: Resolves naming conflicts
- `onomatool/renamer.py`: Performs file renaming operations
- `onomatool/llm_integration.py`: Dummy LLM implementation for Phase 1
## Updated File Tree
```
.
├── ARCHITECTURE.md
├── CHANGELOG.md
├── FILETREE.md
├── requirements.txt
└── onomatool
    ├── __init__.py
    ├── cli.py
    ├── config.py
    ├── conflict_resolver.py
    ├── file_collector.py
    ├── file_dispatcher.py
    ├── llm_integration.py
    ├── renamer.py
    └── processors
        ├── __init__.py
        ├── markitdown_processor.py
        └── text_processor.py
```

- src/onomatool/llm_integration.py  # LLM API integration, now detects .svg as image for LLM input
- src/onomatool/cli.py  # CLI logic, now uses convert_svg_to_png utility for SVGs before LLM input
- src/onomatool/utils/image_utils.py  # Utility for SVG-to-PNG conversion (max 1024px, aspect ratio preserved)
- src/onomatool/processors/markitdown_processor.py  # No longer handles SVG-to-PNG conversion

# Notes
- SVG files are always converted to PNG before being sent to the LLM, using the convert_svg_to_png utility. The PNG is stored in a temporary directory and deleted after processing.
- The application enforces that only PNGs are sent to the LLM, never raw SVGs, and always with the correct MIME type.
- Temporary files and directories for image conversions are always cleaned up, even on exceptions.
- If SVG-to-PNG conversion fails, the file is skipped and an error is reported.

# Updates
- src/onomatool/cli.py: Added --debug CLI option. When set, disables deletion of temp files for SVG, PDF, PPTX and prints their paths.
- src/onomatool/file_dispatcher.py: Accepts debug argument, passes to MarkitdownProcessor.
- src/onomatool/processors/markitdown_processor.py: Accepts debug argument, prints tempdir and image paths for PDF/PPTX when debug is True.