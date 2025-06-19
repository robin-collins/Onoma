#!/bin/bash
set -e

echo "🏗️  Building Onomatool package..."

# Activate project virtual environment
echo "🐍 Activating project virtual environment..."
if [ ! -d ".venv" ]; then
    echo "❌ Error: .venv directory not found. Please create the virtual environment first:"
    echo "   uv venv --python 3.13"
    echo "   source .venv/bin/activate"
    echo "   uv pip install -r requirements.txt"
    exit 1
fi
source .venv/bin/activate

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ src/onomatool.egg-info/

# Install build dependencies
echo "📦 Installing build dependencies..."
uv pip install --upgrade build twine

# Run linting and formatting
echo "🔍 Running code quality checks..."
ruff check src/
ruff format src/

# Build the package
echo "🔨 Building package..."
python -m build

# Verify the package
echo "✅ Verifying package..."
twine check dist/*

echo "🎉 Build complete! Distribution files:"
ls -la dist/

echo ""
echo "📋 To publish to PyPI:"
echo "   Test PyPI: twine upload --repository testpypi dist/*"
echo "   Real PyPI: twine upload dist/*"
echo ""
echo "💡 Virtual environment remains active for publishing commands"