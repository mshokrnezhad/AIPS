#!/bin/bash
# Install AIPS as a global command

echo "📦 Installing AIPS Command"
echo "=========================="
echo ""

# Determine installation directory
INSTALL_DIR="$HOME/.local/bin"
COMMAND_NAME="aips"

# Create directory if it doesn't exist
if [ ! -d "$INSTALL_DIR" ]; then
    echo "Creating $INSTALL_DIR..."
    mkdir -p "$INSTALL_DIR"
fi

# Copy the script
echo "Installing command to $INSTALL_DIR/$COMMAND_NAME..."
cp aips-run.sh "$INSTALL_DIR/$COMMAND_NAME"
chmod +x "$INSTALL_DIR/$COMMAND_NAME"

# Check if directory is in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo ""
    echo "⚠️  $INSTALL_DIR is not in your PATH"
    echo ""
    echo "Add this line to your ~/.bashrc or ~/.bash_profile:"
    echo ""
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "Then run: source ~/.bashrc"
else
    echo ""
    echo "✅ Installation complete!"
    echo ""
    echo "You can now run 'aips' from any directory!"
fi

echo ""
echo "Usage:"
echo "  cd /path/to/your/project"
echo "  aips"
echo ""
