# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OnomaTool is an AI-powered file renaming tool that uses LLMs (OpenAI/Google Gemini) to generate intelligent filename suggestions. It processes various file types (PDFs, images, documents, SVGs, etc.) by extracting content and using AI to suggest meaningful names following configurable naming conventions.

## Development Commands

**Note**: This project uses the `uv` package manager for dependency management and task execution. Install it with `pip install uv` or follow the [official installation guide](https://docs.astral.sh/uv/getting-started/installation/).

### Core Commands
- `uv pip install -e .`: Install the package in development mode
- `onomatool --save-config`: Generate default configuration file
- `uv run pytest`: Run the test suite
- `uv run pytest tests/test_usage_enduser.py`: Run end-to-end user tests
- `uv run pytest tests/test_utf8_encoding.py`: Run UTF-8 encoding tests
- `uv run pytest --cov=onomatool`: Run tests with coverage

### Code Quality
- `ruff check --fix .`: Run linter and auto-fix issues
- `ruff format .`: Format code
- `./scripts/check-format.sh`: Run import sorting and formatting
- `ruff check . && ruff format --check .`: Validate code style

### Testing Individual Components
- `uv run pytest tests/test_config.py`: Test configuration system
- `uv run pytest tests/test_conflict_resolver.py`: Test filename conflict resolution
- `uv run pytest tests/test_file_collector.py`: Test file collection/globbing
- `uv run pytest tests/test_renamer.py`: Test file renaming logic

## Architecture Overview

The tool follows a modular pipeline architecture:

1. **CLI Interface** (`cli.py`) - Handles command-line arguments and orchestrates the workflow
2. **File Collector** (`file_collector.py`) - Processes glob patterns to find target files
3. **File Dispatcher** (`file_dispatcher.py`) - Routes files to appropriate processors based on type
4. **Processors** (`processors/`) - Extract content from different file types:
   - `markitdown_processor.py` - Handles PDFs, DOCX, PPTX using Markitdown library
   - `text_processor.py` - Processes text files with encoding detection
5. **LLM Integration** (`llm_integration.py`) - Communicates with OpenAI/Google APIs
6. **Conflict Resolver** (`conflict_resolver.py`) - Handles filename conflicts with numeric suffixes
7. **Renamer** (`renamer.py`) - Performs actual file renaming operations

### Key Processing Flow
- SVG files are converted to PNG for AI analysis
- PDFs/PPTX generate both text content and page/slide images
- Text files use automatic UTF-8 encoding detection and conversion
- All processors return markdown content for LLM analysis
- LLM generates 3 filename suggestions following configured naming convention
- Conflict resolution ensures no file overwrites

## Configuration System

- Main config file: `~/.onomarc` (TOML format)
- Supports both OpenAI and Google Gemini providers
- Configurable naming conventions: snake_case, CamelCase, kebab-case, PascalCase, dot.notation, natural language
- Word count limits for filename generation (min/max words)
- Custom prompts for different content types
- Local LLM endpoint support via `openai_base_url`

## File Processing Capabilities

- **Documents**: PDF, DOCX, PPTX (via Markitdown + image extraction)
- **Images**: JPG, PNG, etc. (base64 encoding for direct AI analysis)
- **SVG**: Converted to PNG for processing
- **Text**: TXT, MD, CSV, JSON, XML, HTML (with encoding detection)
- **Code**: PY, JS, CSS, YAML (UTF-8 processing)

## Safety Features

- **Dry-run mode**: Preview changes without modifying files
- **Interactive mode**: Confirmation after dry-run
- **Debug mode**: Preserve temporary files for inspection
- **No overwrites**: Built-in conflict resolution
- **Extension preservation**: Original extensions always maintained
- **Encoding safety**: Automatic UTF-8 conversion preserves originals

## Testing Strategy

The project has comprehensive tests covering:
- End-to-end user workflows (`test_usage_enduser.py`)
- UTF-8 encoding detection and conversion (`test_utf8_encoding.py`)
- Individual component functionality
- Configuration handling
- Error conditions and edge cases

## Development Notes

- Python 3.10+ required
- Uses the `uv` package manager for dependency management and task execution
- Uses setuptools build system with `pyproject.toml`
- Entry point: `onomatool.cli:console_script`
- Follows PEP 8 conventions with Ruff for linting/formatting
- Modular architecture allows easy extension of file processors
- Comprehensive error handling with graceful failures
- Supports both local and cloud LLM endpoints

### Package Manager Usage
- Install dependencies: `uv pip install -r requirements.txt`
- Install development dependencies: `uv pip install -e .`
- Run commands: `uv run <command>` (e.g., `uv run pytest`)
- Sync dependencies: `uv pip sync requirements.txt`