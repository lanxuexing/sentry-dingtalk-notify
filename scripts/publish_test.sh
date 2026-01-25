#!/bin/bash
# scripts/publish_test.sh
# Publishes the package to TestPyPI

# Exit immediately if a command exits with a non-zero status.
set -e

# get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# set project root
PROJECT_ROOT="$DIR/.."

cd "$PROJECT_ROOT"

echo "----------------------------------------------------------------"
echo "🚀 Starting TestPyPI Publish Process"
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

# 4. Upload to TestPyPI
echo "uploading to TestPyPI..."
echo "Note: You need a TestPyPI account and a token (or username/password)."
echo "      Register at: https://test.pypi.org/account/register/"

twine upload --repository testpypi dist/*

echo "----------------------------------------------------------------"
echo "✅ Done! Verify at https://test.pypi.org/project/sentry-dingtalk-notify/"
echo "----------------------------------------------------------------"
