#!/bin/bash
# Uninstall AIPS global command

echo "🗑️  Uninstalling AIPS Command"
echo "============================="
echo ""

INSTALL_DIR="$HOME/.local/bin"
COMMAND_NAME="aips"

if [ -f "$INSTALL_DIR/$COMMAND_NAME" ]; then
    rm "$INSTALL_DIR/$COMMAND_NAME"
    echo "✅ AIPS command removed from $INSTALL_DIR"
else
    echo "⚠️  AIPS command not found in $INSTALL_DIR"
fi

echo ""
