#!/bin/bash
# Run AIPS Docker container

echo "🚀 Running AIPS Docker Container"
echo "================================="
echo ""

# Check if urls.json exists (either in current dir or data/ dir)
if [ ! -f "urls.json" ] && [ ! -f "data/urls.json" ]; then
    echo "⚠️  Warning: urls.json not found!"
    echo "   Expected location: ./urls.json or ./data/urls.json"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "✗ docker-compose.yml not found!"
    exit 1
fi

# Check if image exists
if ! docker images | grep -q "aips"; then
    echo "⚠️  Docker image not found!"
    echo "   Please build the image first: ./build.sh"
    exit 1
fi

echo "Starting AIPS container..."
echo ""

# Run the container
docker compose up

echo ""
echo "✅ Done!"
