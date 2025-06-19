# 🎉 OnomaTool: AI-Powered File Renamer 🚀

![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)
![License](https://img.shields.io/badge/license-MIT-green)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)
![Tests Passing](https://img.shields.io/badge/tests-passing-success?logo=pytest)

---

## ✨ What is OnomaTool?

**OnomaTool** is your AI-powered file renaming assistant! 🧠✨

- Rename files in bulk with smart, context-aware suggestions 🤖
- Supports PDFs, images, markdown, SVG, PPTX, DOCX, TXT, and more! 📄🖼️
- Always preserves file extensions 🔒
- CLI with dry-run, interactive, verbose, and debug modes 🖥️
- Configurable via `.onomarc` TOML config file ⚙️
- Uses Markitdown for unified file processing 📝
- **NEW**: Advanced UTF-8 encoding detection and conversion for text files 🔤
- **NEW**: Configurable word count limits for filenames 🔤

---

## 🚀 Features

### Core Functionality
- 🦾 **AI Suggestions**: Get 3 smart file name ideas for every file
- 🤖 **Multiple LLM Providers**: OpenAI (including local endpoints) and Google Gemini support
- 🧩 **Conflict Resolution**: Never overwrite files - automatic numeric suffix handling
- 🔒 **Extension Preservation**: Original file extensions are always preserved
- 📁 **Glob Pattern Support**: Process files using flexible glob patterns

### File Processing
- 📄 **PDF Files**: Extract markdown content + generate images for each page
- 🖼️ **SVG Files**: Convert to PNG for AI analysis (enforced PNG-only processing)
- 📊 **PPTX Files**: Extract content + generate images for each slide using LibreOffice
- 📝 **Text Files**: UTF-8 encoding detection and conversion + markdown processing
- 🖼️ **Image Files**: Base64 encoding for direct AI image analysis
- 📑 **Office Documents**: DOCX, XLSX support via Markitdown
- 🔤 **Unicode Support**: Automatic encoding detection for text files with chardet

### CLI Modes
- 🧪 **Dry-Run Mode**: Preview changes without modifying files (`--dry-run`)
- 🤝 **Interactive Mode**: Confirm changes after dry-run preview (`--interactive`)
- 🔍 **Debug Mode**: Preserve temp files and show processing paths (`--debug`)
- 📢 **Verbose Mode**: Show LLM requests and responses (`--verbose`)
- ⚙️ **Config Generation**: Generate default config file (`--save-config`)

### Advanced Features
- 🎯 **Smart Processing**: Combined image + text analysis for documents
- 🏗️ **Modular Architecture**: Extensible processor system
- 🌐 **Local LLM Support**: Works with local OpenAI-compatible endpoints
- 📊 **Multiple Naming Conventions**: snake_case, CamelCase, kebab-case, and more
- 🛡️ **SSL Flexibility**: Automatic SSL handling for local/HTTP endpoints
- 🔤 **Encoding Intelligence**: Automatic detection and UTF-8 conversion for text files
- 🧪 **Comprehensive Testing**: 13+ test cases for encoding reliability

---

## 🛠️ Installation

### Method 1: Install from Source
```bash
# Clone the repository
git clone https://github.com/yourusername/onomatool.git
cd onomatool

# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For encoding detection (included in requirements.txt)
pip install chardet

# Install the package
pip install -e .
```

### Method 2: Direct Installation
```bash
# Install directly from the repository
pip install git+https://github.com/yourusername/onomatool.git
```

### System Dependencies
For full functionality (SVG, PDF, PPTX processing):
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install libreoffice imagemagick libcairo2 libpango-1.0-0 libpangocairo-1.0-0

# macOS (with Homebrew)
brew install libreoffice imagemagick cairo pango

# Windows: Download and install LibreOffice and ImageMagick
# For SVG support: pip install cairosvg (requires Cairo system libraries)
```

---

## ⚡ Quick Start

### Basic Usage
```bash
# Rename all PDFs in current directory
onomatool '*.pdf'

# Process files in subdirectories
onomatool 'docs/**/*.md'

# Specify file format explicitly
onomatool '*.unknown' --format pdf
```

### Preview Mode
```bash
# See what would be renamed (no changes made)
onomatool '*.jpg' --dry-run

# Interactive confirmation after preview
onomatool '*.pdf' --dry-run --interactive
```

### Debug and Verbose Modes
```bash
# Debug mode - preserve temp files
onomatool '*.svg' --debug

# Verbose mode - see LLM interactions
onomatool '*.docx' --verbose

# Combined modes
onomatool '*.pptx' --debug --verbose --dry-run
```

---

## ⚙️ Configuration

OnomaTool uses a TOML configuration file at `~/.onomarc` or a custom path with `--config`.

### Generate Default Config
```bash
onomatool --save-config
```

### Configuration Options
```toml
# API Configuration
default_provider = "openai"  # or "google"
openai_api_key = "sk-..."
openai_base_url = "https://api.openai.com/v1"  # or local endpoint
google_api_key = "your-google-api-key"

# Model and Behavior
llm_model = "gpt-4o"  # or "gemini-pro"
naming_convention = "snake_case"  # snake_case, CamelCase, kebab-case, etc.

# Custom Prompts (optional - defaults provided)
system_prompt = "You are a file naming assistant."
user_prompt = "Suggest 3 file names for: {content}"
image_prompt = "Suggest 3 file names for this image."

# Markitdown Configuration
[markitdown]
enable_plugins = false
docintel_endpoint = ""

# Word count limits (NEW!)
min_filename_words = 5      # Minimum words required (ensures descriptive names)
max_filename_words = 15     # Maximum words allowed (prevents overly long names)
```

### Supported Naming Conventions
- `snake_case` (default)
- `CamelCase`
- `kebab-case`
- `PascalCase`
- `dot.notation`
- `natural language`

---

## 📁 Supported File Types

| File Type | Processing Method | Output |
|-----------|-------------------|---------|
| PDF | Markitdown + PyMuPDF page images | Combined text + image analysis |
| PPTX | Markitdown + LibreOffice slide images | Combined text + image analysis |
| SVG | Convert to PNG + Markitdown | Image analysis only |
| Images (JPG, PNG, etc.) | Base64 encoding | Direct image analysis |
| DOCX | Markitdown processing | Text analysis |
| TXT, MD, NOTE | UTF-8 encoding detection + text processing | Text analysis |
| XLSX | Markitdown processing | Content analysis |
| CSV, JSON, XML, HTML | UTF-8 encoding detection + Markitdown | Content analysis |
| Code Files (PY, JS, CSS, YAML) | UTF-8 encoding detection + text processing | Code analysis |

---

## 🧑‍💻 Development

### Project Structure
```
src/onomatool/
├── cli.py                 # Command-line interface
├── config.py              # Configuration management
├── llm_integration.py     # OpenAI/Google API integration
├── file_dispatcher.py     # File routing logic
├── processors/            # File processing modules
│   ├── markitdown_processor.py
│   └── text_processor.py
├── utils/                 # Utility functions
│   └── image_utils.py     # SVG conversion utilities
├── prompts.py             # Default prompts
├── renamer.py             # File renaming logic
├── conflict_resolver.py   # Filename conflict handling
└── file_collector.py      # Glob pattern matching
```

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-mock

# Run all tests
pytest

# Run specific test suites
pytest tests/test_usage_enduser.py    # End-to-end user tests
pytest tests/test_utf8_encoding.py    # UTF-8 encoding tests

# Run with coverage
pytest --cov=onomatool
```

### Code Style
```bash
# Format code
ruff format .

# Lint code
ruff check --fix .

# Run all checks
ruff check . && ruff format --check .
```

---

## 🔧 Advanced Usage

### Custom Configuration Files
```bash
# Use custom config file
onomatool '*.pdf' --config /path/to/custom.toml
```

### Local LLM Endpoints
```toml
# In your .onomarc
default_provider = "openai"
openai_base_url = "http://localhost:1234/v1"
openai_api_key = "not-needed-for-local"
```

### Processing Specific Formats
```bash
# Force format detection
onomatool 'unknown_files/*' --format pdf
onomatool 'images/*' --format image
```

---

## 🛡️ Safety Features

- **No Overwrites**: Built-in conflict resolution with numeric suffixes
- **Extension Preservation**: Original file extensions always maintained
- **Dry-Run Mode**: Preview all changes before execution
- **Temp File Management**: Automatic cleanup (preservable in debug mode)
- **Error Handling**: Graceful failure with clear error messages
- **Encoding Safety**: Automatic UTF-8 conversion preserves original files
- **Unicode Compatibility**: Handles em dashes, smart quotes, accented characters

---

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository 🍴
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes 🧪
4. Follow PEP8 and run `ruff check --fix .` 🐍
5. Update `CHANGELOG.md` and `FILETREE.md` 📚
6. Submit a pull request 🚀

### Development Setup
```bash
# Clone and setup development environment
git clone https://github.com/yourusername/onomatool.git
cd onomatool
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Install development dependencies
pip install pytest pytest-mock ruff

# Run tests to verify setup
pytest tests/test_utf8_encoding.py
pytest tests/test_usage_enduser.py
```

---

## 📜 License

MIT License - see LICENSE file for details.

---

## 🙋 FAQ

**Q: Does it work on Windows/Mac/Linux?**
A: Yes! Cross-platform support with Python 3.10+.

**Q: Can I use local LLMs?**
A: Yes! Set `openai_base_url` to your local endpoint in `.onomarc`.

**Q: Will it overwrite my files?**
A: Never! Built-in conflict resolution prevents overwrites.

**Q: What if my API key is invalid?**
A: The tool will show clear error messages and fail gracefully.

**Q: Can I customize the AI prompts?**
A: Yes! Set `system_prompt`, `user_prompt`, and `image_prompt` in your config.

**Q: How does SVG processing work?**
A: SVGs are converted to PNG images before AI analysis for better results.

**Q: Can I see what the AI is thinking?**
A: Use `--verbose` to see full LLM requests and responses.

**Q: What about files with special characters or different encodings?**
A: OnomaTool automatically detects and converts file encodings to UTF-8, handling em dashes, accented characters, and other Unicode symbols seamlessly.

**Q: Does it work with files that have encoding issues?**
A: Yes! The tool uses advanced encoding detection to identify and convert problematic files while preserving the original content.

**Q: How do word count limits affect filename generation?**
A: Word count limits control the minimum and maximum number of words in generated filenames. This helps maintain descriptive and concise naming conventions.

---

## 🌟 Star this repo if you find it useful! 🌟

> Made with ❤️, AI, and a lot of `import os`.