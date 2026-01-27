#!/bin/bash
# Standalone AIPS runner - can be copied to any folder
# Requires: AIPS Docker image already built

echo "🚀 Running AIPS"
echo "==============="
echo ""
echo "Working directory: $(pwd)"
echo ""

# Check if urls.json exists in current directory
if [ ! -f "urls.json" ]; then
    echo "⚠️  Warning: urls.json not found in current directory!"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if AIPS image exists
if ! docker images | grep -q "aips"; then
    echo "✗ AIPS Docker image not found!"
    echo "   Please build it first from the AIPS project folder:"
    echo "   cd /path/to/AIPS && ./build.sh"
    exit 1
fi

echo "Starting AIPS with files from current directory..."
echo ""

# Run container with current directory mounted
docker run --rm \
    -v "$(pwd):/data" \
    -w /data \
    aips

echo ""
echo "✅ Done!"
echo "Check venue folders in: $(pwd)"
