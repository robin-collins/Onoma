# Changelog

## [Documentation Update] - 2025-01-27
### Updated
- Completely rewrote README.md to accurately reflect current application features and functionality
- Added comprehensive feature breakdown including Core Functionality, File Processing, CLI Modes, and Advanced Features
- Updated installation instructions with multiple installation methods
- Added detailed configuration examples with all supported options
- Added supported file types table showing processing methods and outputs
- Added development section with project structure, testing, and code style information
- Added advanced usage examples for custom configs, local LLMs, and format forcing
- Added safety features section highlighting conflict resolution and data protection
- Updated FAQ section with more comprehensive questions and answers
- Improved overall organization and readability with better section structure

## [Architecture Redesign] - 2025-06-15
### Implemented
- Integrated Markitdown as primary file processor
- Deprecated PyPDF2, python-docx, openpyxl, python-pptx and pdf2image
- Added Markitdown configuration options
- Updated implementation roadmap

### Changed
- Simplified processing pipeline to use single Markitdown processor
- Updated architecture diagrams in ARCHITECTURE.md
- Maintained text processor for .txt/.md files

## [Phase 1] - 2025-06-15
### Implemented
- Core CLI functionality with argparse
- File collector with glob pattern support
- Text file processor for .txt and .md files
- Conflict resolver with numeric suffix fallback
- File renamer using conflict resolution
- Replaced dummy LLM integration in llm_integration.py with real OpenAI/Google LLM API calls using JSON schema for filename suggestions, as per ARCHITECTURE.md and lmstudio-structured-output-example.md.
- Added `--save-config` option to generate default configuration file
- Improved CLI help output with detailed descriptions and examples

## [Previous]
- Added 'maxLength: 128' to the string items in all filename suggestion JSON schemas (snake_case, CamelCase, kebab-case, PascalCase, dot.notation, and natural language) in ARCHITECTURE.md to enforce a maximum filename length constraint.

## [Phase 2] - 2025-06-15
### Added
- Markitdown processor for unified file processing
- Configuration options for markitdown (provider, API keys, image descriptions)
### Changed
- File dispatcher to use markitdown processor
- CLI to support format argument and new configuration
### Removed
- Obsolete processors (PDF, DOCX, XLSX, PPTX) - replaced by markitdown
### Dependencies
- Added markitdown and toml packages
- Added openai and google-generativeai to requirements.txt

## [Fixed] - 2025-06-15
### Fixed
- Fix: Temp files for PDF/SVG/PPTX are now properly preserved when running with --debug. Fixed variable collision issue where PDF tempdir was overwriting SVG tempdir variable, causing incorrect cleanup behavior. Temp directories are now kept alive for the duration of the program to prevent garbage collection, and debug output shows preservation status.

### Enhanced
- Enhancement: When using --debug mode, the markdown content extracted by MarkItDown from ALL file types (PDF, PPTX, DOCX, TXT, etc.) is now saved as "extracted_content.md" in dedicated temp directories alongside any images, allowing for complete inspection of the extracted content for any file type.

## [New] - 2025-06-15
### Added
- OpenAI integration now supports local endpoints and disables SSL verification for local or http URLs, with a warning message.
- Added --verbose CLI option to print the LLM request and response for debugging.
- File renaming now always preserves the original file extension, regardless of LLM suggestion.
- System and user prompts are now configurable via .onomarc and managed in prompts.py. The LLM integration uses these prompts for all requests.
- The default config now includes system_prompt and user_prompt as empty strings, so users can override or leave them empty to use the built-in defaults.
- llm_model is now in the main config section, is saved by default, and all naming convention schemas from ARCHITECTURE.md are now supported.
- Added --dry-run CLI option, which prints intended renames (with conflict resolution and extension preservation) without modifying any files.
- Added --interactive option, which works with --dry-run to prompt for confirmation and then perform the planned renames using the suggestions from the dry-run (no new LLM calls).
- Image files are now base64 encoded and sent as OpenAI image inputs when using the OpenAI provider, following the OpenAI API example.
- image_prompt is now supported in the config and used for image renaming, with a default provided in prompts.py. The --save-config default now includes image_prompt.
- PDF files are now processed by extracting markdown via Markitdown and generating images for each page using PyMuPDF. Each page image is sent to the LLM for suggestions, then the markdown is sent, and finally a combined prompt is used to generate the final suggestions.
- PPTX files are now processed by extracting markdown via Markitdown and generating images for each slide using python-pptx and Pillow. Each slide image is sent to the LLM for suggestions, then the markdown is sent, and finally a combined prompt is used to generate the final suggestions.
- SVG files are now rendered to PNG (longest side 1024px, aspect ratio preserved) using cairosvg and Pillow, and processed as images for LLM suggestions.
- Enforced that only PNGs (never raw SVGs) are sent to the LLM, with explicit PNG MIME type.
- Added a guard to raise an error if a raw SVG is ever sent to the LLM.
- Improved temporary directory cleanup for image conversions (including SVG-to-PNG) to always clean up, even on exceptions.
- Refactored SVG-to-PNG conversion: now handled by a dedicated utility (convert_svg_to_png in utils/image_utils.py), not in MarkitdownProcessor.
- The CLI now always uses this utility for SVGs before LLM input, and never sends raw SVGs to the LLM.
- Errors in SVG-to-PNG conversion are reported and the file is skipped.

### [Added] - 2025-06-16
* Added `--debug` CLI option. When set, temporary files and directories created for SVG, PDF, and PPTX processing are not deleted after use, and their full paths are printed to the console for debugging.
* FileDispatcher and MarkitdownProcessor now accept a debug argument to control debug output and temp file cleanup behavior.

## [Added] - 2025-06-17
- Added end user usage tests in tests/test_usage_enduser.py for CLI, --config, dry-run, interactive, debug, and config override features. Tests use pytest and mock LLM responses.
- Added test_files/mock_config.toml for use in tests, with static LLM responses and simple prompts.
