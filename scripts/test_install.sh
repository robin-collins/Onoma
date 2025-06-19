#!/bin/bash
set -e

echo "🧪 Testing Onomatool installation..."

# Activate project virtual environment
echo "🐍 Activating project virtual environment..."
if [ ! -d ".venv" ]; then
    echo "❌ Error: .venv directory not found. Please create the virtual environment first:"
    echo "   python -m venv .venv"
    echo "   source .venv/bin/activate"
    echo "   uv pip install -r requirements.txt"
    exit 1
fi
source .venv/bin/activate

# Create a temporary virtual environment for isolated testing
TEMP_VENV=$(mktemp -d)/test_venv
echo "📁 Creating temporary test venv: $TEMP_VENV"
python -m venv "$TEMP_VENV"
source "$TEMP_VENV/bin/activate"

# Install uv in the test environment
echo "📦 Installing uv in test environment..."
pip install uv

# Install the built package
echo "📦 Installing from dist/..."
uv pip install dist/*.whl

# Test the CLI command is available
echo "🔍 Testing CLI availability..."
which onomatool
onomatool --help

# Test basic functionality with mock provider
echo "🎯 Testing basic functionality..."
mkdir -p /tmp/onomatool_test
cd /tmp/onomatool_test
echo "This is a test file for onomatool" > test_file.txt

# Create a test config with mock provider
cat > test_config.toml << EOF
default_provider = "mock"
naming_convention = "snake_case"
EOF

# Test dry run
onomatool --config test_config.toml --dry-run "*.txt"

# Cleanup
echo "🧹 Cleaning up..."
rm -rf /tmp/onomatool_test
deactivate  # Deactivate test venv
rm -rf "$TEMP_VENV"

# Reactivate project venv
source .venv/bin/activate

echo "✅ Installation test passed!"