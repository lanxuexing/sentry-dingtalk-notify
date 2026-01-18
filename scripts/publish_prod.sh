#!/bin/bash
# scripts/publish_prod.sh
# Publishes the package to PyPI (Production)

# Exit immediately if a command exits with a non-zero status.
set -e

# get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# set project root
PROJECT_ROOT="$DIR/.."

cd "$PROJECT_ROOT"

echo "----------------------------------------------------------------"
echo "🚀 Starting Production PyPI Publish Process"
echo "----------------------------------------------------------------"

# 1. Clean previous builds
echo "🧹 Cleaning up previous builds..."
rm -rf dist/ build/ *.egg-info

# 2. Build the package
echo "📦 Building Source and Wheel distribution..."
python3 setup.py sdist bdist_wheel --universal

# 3. Check for Twine
if ! command -v twine &> /dev/null
then
    echo "❌ Error: Twine is not installed."
    echo "   Please run: pip install twine"
    exit 1
fi

# 4. Upload to PyPI
echo "uploading to PyPI..."
echo "Note: You need a PyPI account and a token (or username/password)."
echo "      Also ensure you have bumped the version in setup.py and plugin.py!"

twine upload dist/*

echo "----------------------------------------------------------------"
echo "✅ Done! Verify at https://pypi.org/project/sentry-dingtalk-notify/"
echo "----------------------------------------------------------------"
