#!/bin/bash
# Deploy horror theme login page
# Run this on the Pi: sudo bash deploy_horror_theme.sh

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
HTML_DIR="/var/www/html/theblackbox"

echo "=== Deploying Horror Theme ==="

# 1. Copy login page
echo "Copying login.html..."
cp "$REPO_DIR/login.html" "$HTML_DIR/"

# 2. Copy Creepster font
echo "Copying Creepster font..."
cp "$REPO_DIR/Creepster-Regular.ttf" "$HTML_DIR/"

# 3. Copy clown image for flash effect
echo "Copying clown.jpg..."
cp "$REPO_DIR/clown.jpg" "$HTML_DIR/"

# 4. Also update the copy in /opt/theblackbox/html/ if it exists
if [ -d "/opt/theblackbox/html" ]; then
    echo "Also updating /opt/theblackbox/html/..."
    cp "$REPO_DIR/login.html" "/opt/theblackbox/html/"
    cp "$REPO_DIR/Creepster-Regular.ttf" "/opt/theblackbox/html/"
    cp "$REPO_DIR/clown.jpg" "/opt/theblackbox/html/"
fi

echo ""
echo "=== Done! ==="
echo "Refresh Firefox with: DISPLAY=:0 xdotool key F5"
echo "Or full restart with: restart"
