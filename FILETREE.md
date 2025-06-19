# Onoma Project File Structure

## Current Project Structure

```
.
├── .cursorignore
├── .gitignore
├── ARCHITECTURE.md              # System architecture documentation
├── AZURE_OPENAI_SETUP.md        # Azure OpenAI configuration guide
├── CHANGELOG.md                 # Change history and version notes
├── FILETREE.md                  # This file - project structure overview
├── LICENSE                      # MIT license for open source distribution
├── MANIFEST.in                  # Files to include in PyPI package
├── README.md                    # Main project documentation
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Complete PyPI packaging configuration
├── scripts/
│   ├── build.sh                 # Automated PyPI package build script
│   ├── check-format.sh          # Code formatting check script
│   └── test_install.sh          # Installation verification script
├── src/
│   └── onomatool/
│       ├── __init__.py          # Package initialization
│       ├── cli.py               # Command-line interface and main entry point
│       ├── config.py            # Configuration management (.onomarc handling)
│       ├── file_collector.py    # Glob pattern file collection
│       ├── file_dispatcher.py   # Routes files to appropriate processors
│       ├── llm_integration.py   # OpenAI/Google API integration
│       ├── models.py            # Pydantic models for structured LLM responses
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
    ├── test_utf8_encoding.py     # UTF-8 encoding detection and conversion tests
    └── test_files/
        └── mock_config.toml      # Test configuration with mock LLM responses
```

## Key Components

### Core CLI Module
- **`src/onomatool/cli.py`**: Main entry point with argument parsing, mode handling (dry-run, interactive, debug, verbose), and orchestration of the entire file processing pipeline

### Configuration System
- **`src/onomatool/config.py`**: Handles `.onomarc` TOML configuration loading with fallback to defaults
  - New options: `min_filename_words` (default: 5) and `max_filename_words` (default: 15)
  - Configurable word count limits for all naming conventions
  - Azure OpenAI integration support with dedicated configuration options
- **`src/onomatool/prompts.py`**: Centralized prompt management with configurable system/user/image prompts
- **`AZURE_OPENAI_SETUP.md`**: Comprehensive guide for configuring Azure OpenAI services

### File Processing Pipeline
- **`src/onomatool/file_collector.py`**: Glob pattern matching for file discovery
- **`src/onomatool/file_dispatcher.py`**: Routes files to appropriate processors based on file type
- **`src/onomatool/processors/markitdown_processor.py`**: Primary processor using Markitdown library with UTF-8 encoding support and special handling for:
  - Text files: Automatic encoding detection and UTF-8 conversion using chardet
  - PDF files: Extract markdown + generate page images via PyMuPDF
  - PPTX files: Extract markdown + generate slide images via LibreOffice/ImageMagick
  - DOCX, XLSX, TXT files: Direct Markitdown processing with encoding safety
  - Debug mode support with temp file preservation and encoding diagnostics
- **`src/onomatool/processors/text_processor.py`**: Lightweight processor for simple text files

### LLM Integration
- **`src/onomatool/llm_integration.py`**:
  - OpenAI API integration with local endpoint support
  - **Azure OpenAI API integration** with AzureOpenAI client support
  - Automatic provider switching based on `use_azure_openai` configuration flag
  - Azure deployment name handling and API version management
  - Environment variable support for Azure configuration
  - **Pydantic Structured Output**: Uses `client.beta.chat.completions.parse()` with type-safe Pydantic models
  - Automatic fallback to JSON schema if structured output fails
  - Google Gemini API integration
  - Image processing (base64 encoding for OpenAI/Azure OpenAI)
  - SSL handling for local/HTTP endpoints
  - Token limit control: `MAX_TOKENS = 100` constant for response length control
  - Consistent token limiting across OpenAI, Azure OpenAI, and Google providers
  - Enhanced verbose mode with provider-specific debugging and Pydantic model information
- **`src/onomatool/models.py`**:
  - **Pydantic Models**: Type-safe models for all naming conventions with built-in validation
  - Individual models for each format: `SnakeCaseFilenameSuggestions`, `CamelCaseFilenameSuggestions`, etc.
  - Automatic JSON schema generation from Pydantic models for fallback compatibility
  - Format validation ensuring suggestions match naming convention patterns
  - Utility functions for model selection and schema generation

### Utilities
- **`src/onomatool/utils/image_utils.py`**: SVG-to-PNG conversion with Cairo/Pillow, maintaining aspect ratio at max 1024px

### File Operations
- **`src/onomatool/conflict_resolver.py`**: Prevents file overwrites with intelligent numeric suffix handling
- **`src/onomatool/renamer.py`**: Executes file renaming with conflict resolution

## Special Processing Workflows

### Text File Encoding Handling
1. Automatic encoding detection using chardet library for text files
2. Supported text extensions: .txt, .md, .note, .text, .log, .csv, .json, .xml, .html, .htm, .py, .js, .css, .yaml, .yml
3. Create temporary UTF-8 copies for non-UTF-8 files with graceful error handling
4. Preserve original files unchanged while processing UTF-8 versions
5. Automatic cleanup of temporary files after processing
6. Debug mode provides encoding detection diagnostics

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