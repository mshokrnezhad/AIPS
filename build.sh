#!/bin/bash
# Build Docker image for AIPS

echo "🔨 Building AIPS Docker Image"
echo "=============================="
echo ""

# Check if required files exist
if [ ! -f "Dockerfile" ]; then
    echo "✗ Dockerfile not found!"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   The Docker image will not have API keys."
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

if [ ! -f "requirements.txt" ]; then
    echo "✗ requirements.txt not found!"
    exit 1
fi

echo "Building Docker image..."
echo ""

# Build the image
docker-compose build

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Docker image built successfully!"
    echo ""
    echo "Next step: Run the container with ./run.sh"
else
    echo ""
    echo "✗ Build failed!"
    exit 1
fi
