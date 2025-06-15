# 🎉 OnomaTool: AI-Powered File Renamer 🚀

![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)
![License](https://img.shields.io/badge/license-MIT-green)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)
![Tests Passing](https://img.shields.io/badge/tests-passing-success?logo=pytest)

---

## ✨ What is OnomaTool?

**OnomaTool** is your AI-powered file renaming assistant! 🧠✨

- Rename files in bulk with smart, context-aware suggestions 🤖
- Handles PDFs, images, markdown, SVG, PPTX, and more! 📄🖼️
- Always preserves file extensions 🔒
- CLI with dry-run, interactive, and debug modes 🖥️
- Super customizable via `.onomarc` config ⚙️

---

## 🚀 Features

- 🦾 **AI Suggestions**: Get 3 smart file name ideas for every file
- 🖼️ **Image & PDF Support**: Converts SVG/PDF/PPTX to images for better AI context
- 🧩 **Conflict Resolution**: Never overwrite files by accident
- 🧪 **Dry-Run & Interactive**: Preview changes and confirm before renaming
- 🐍 **Pythonic**: Built for Python 3.10+, PEP8/ruff/black compliant
- 🛠️ **Extensible**: Add your own naming conventions and prompts
- 📝 **Comprehensive Logging**: Debug and verbose modes for transparency

---

## 🛠️ Installation

```bash
# 1. Clone the repo
$ git clone https://github.com/yourusername/onomatool.git
$ cd onomatool

# 2. Create a virtual environment (recommended)
$ python3 -m venv .venv
$ source .venv/bin/activate

# 3. Install dependencies
$ pip install -r requirements.txt

# 4. (Optional) Install system dependencies for SVG/PDF/PPTX support
$ sudo apt-get update
$ sudo apt-get install libcairo2 libpango-1.0-0 libpangocairo-1.0-0
```

---

## ⚡ Quick Start

```bash
# Basic usage
$ onomatool '*.pdf'

# Dry-run (see what would be renamed)
$ onomatool '*.jpg' --dry-run

# Interactive mode
$ onomatool '*.md' --dry-run --interactive

# Debug mode (see temp files)
$ onomatool '*.svg' --debug
```

---

## ⚙️ Configuration

OnomaTool uses a TOML config file at `~/.onomarc`.

- Set your API keys, prompts, and naming conventions
- Example:

```toml
[default]
default_provider = "openai"
openai_api_key = "sk-..."
naming_convention = "snake_case"
llm_model = "gpt-4o"
system_prompt = "You are a file naming assistant."
user_prompt = "Suggest 3 file names for: {content}"
image_prompt = "Suggest 3 file names for this image."
```

---

## 🧑‍💻 Contributing

We 💚 contributions! Please:

- Fork the repo 🍴
- Create a feature branch 🌱
- Write clear, PEP8-compliant code 🐍
- Add/Update tests 🧪
- Update `CHANGELOG.md` and `FILETREE.md` 📚
- Submit a PR 🚀

**Code Style:**
- PEP8, ruff, black, and best practices enforced
- Use 4 spaces, 88-char lines, and docstrings
- Run `ruff check --fix .` before PRs

---

## 🏆 Badges & Fun

- 🦾 **AI Inside**: Powered by OpenAI & Google LLMs
- 🦄 **Magic Renames**: Never boring, always smart
- 🛡️ **Safe**: Never overwrites, always preserves extensions
- 🧙‍♂️ **Wizard Mode**: Debug for the curious

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 🙋 FAQ

- **Q:** Does it work on Windows/Mac/Linux?
  **A:** Yes! Cross-platform support.
- **Q:** Can I use my own LLM?
  **A:** Yes! Set your API endpoint in `.onomarc`.
- **Q:** Will it ever overwrite my files?
  **A:** No! Conflict resolution is built-in.

---

## 🌟 Star this repo if you like it! 🌟

> Made with ❤️, 🧠, and a lot of `import os`.