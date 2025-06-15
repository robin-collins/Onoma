# Onoma Project File Structure

## Current Project Structure

```
.
├── .cursorignore
├── .gitignore
├── ARCHITECTURE.md              # System architecture documentation
├── CHANGELOG.md                 # Change history and version notes
├── FILETREE.md                  # This file - project structure overview
├── README.md                    # Main project documentation
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Project configuration and build settings
├── src/
│   └── onomatool/
│       ├── __init__.py          # Package initialization
│       ├── cli.py               # Command-line interface and main entry point
│       ├── config.py            # Configuration management (.onomarc handling)
│       ├── file_collector.py    # Glob pattern file collection
│       ├── file_dispatcher.py   # Routes files to appropriate processors
│       ├── llm_integration.py   # OpenAI/Google API integration
│       ├── conflict_resolver.py # Filename conflict resolution with numeric suffixes
│       ├── renamer.py           # File renaming operations
│       ├── prompts.py           # Default system and user prompts for LLMs
│       ├── processors/
│       │   ├── __init__.py
│       │   ├── markitdown_processor.py  # Unified file processing via Markitdown
│       │   └── text_processor.py        # Simple text file processing (.txt, .md)
│       └── utils/
│           ├── __init__.py
│           └── image_utils.py    # SVG-to-PNG conversion utilities
└── tests/
    ├── __init__.py
    ├── test_usage_enduser.py     # End-to-end user scenario tests
    └── test_files/
        └── mock_config.toml      # Test configuration with mock LLM responses
```

## Key Components

### Core CLI Module
- **`src/onomatool/cli.py`**: Main entry point with argument parsing, mode handling (dry-run, interactive, debug, verbose), and orchestration of the entire file processing pipeline

### Configuration System
- **`src/onomatool/config.py`**: Handles `.onomarc` TOML configuration loading with fallback to defaults
- **`src/onomatool/prompts.py`**: Centralized prompt management with configurable system/user/image prompts

### File Processing Pipeline
- **`src/onomatool/file_collector.py`**: Glob pattern matching for file discovery
- **`src/onomatool/file_dispatcher.py`**: Routes files to appropriate processors based on file type
- **`src/onomatool/processors/markitdown_processor.py`**: Primary processor using Markitdown library with special handling for:
  - PDF files: Extract markdown + generate page images via PyMuPDF
  - PPTX files: Extract markdown + generate slide images via LibreOffice/ImageMagick
  - DOCX, XLSX, TXT files: Direct Markitdown processing
  - Debug mode support with temp file preservation
- **`src/onomatool/processors/text_processor.py`**: Lightweight processor for simple text files

### LLM Integration
- **`src/onomatool/llm_integration.py`**:
  - OpenAI API integration with local endpoint support
  - Google Gemini API integration
  - Image processing (base64 encoding for OpenAI)
  - JSON schema-based filename suggestions
  - SSL handling for local/HTTP endpoints

### Utilities
- **`src/onomatool/utils/image_utils.py`**: SVG-to-PNG conversion with Cairo/Pillow, maintaining aspect ratio at max 1024px

### File Operations
- **`src/onomatool/conflict_resolver.py`**: Prevents file overwrites with intelligent numeric suffix handling
- **`src/onomatool/renamer.py`**: Executes file renaming with conflict resolution

## Special Processing Workflows

### SVG Files
1. Convert to PNG using `convert_svg_to_png` utility
2. Send PNG (never raw SVG) to LLM for analysis
3. Clean up temporary files (preserved in debug mode)

### PDF Files
1. Extract markdown content via Markitdown
2. Generate PNG images for each page via PyMuPDF
3. Send each page image to LLM for individual suggestions
4. Send markdown content to LLM
5. Generate final suggestions combining both inputs

### PPTX Files
1. Extract markdown content via Markitdown
2. Convert to PDF via LibreOffice
3. Convert PDF to JPEG images via ImageMagick
4. Send each slide image to LLM for individual suggestions
5. Send markdown content to LLM
6. Generate final suggestions combining both inputs

## CLI Modes and Features

- **Standard Mode**: Direct file processing and renaming
- **Dry-Run Mode** (`--dry-run`): Preview changes without modification
- **Interactive Mode** (`--interactive`): Confirmation prompts with dry-run
- **Debug Mode** (`--debug`): Preserve temp files and show processing paths
- **Verbose Mode** (`--verbose`): Display LLM request/response details
- **Config Generation** (`--save-config`): Create default `.onomarc` file

## Safety and Error Handling

- Built-in conflict resolution prevents file overwrites
- Original file extensions always preserved
- Graceful error handling with clear messages
- Automatic temp file cleanup (preservable in debug mode)
- SSL verification disabled for local endpoints with warnings

## Testing Infrastructure

- **`tests/test_usage_enduser.py`**: End-to-end testing with mocked LLM responses
- **`tests/test_files/mock_config.toml`**: Test configuration with static responses
- Pytest-based testing framework with mock support