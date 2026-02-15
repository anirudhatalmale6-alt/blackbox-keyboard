#!/bin/bash
# Deploy horror theme + hint system
# Run this on the Pi: sudo bash deploy_horror_theme.sh

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
HTML_DIR="/var/www/html/theblackbox"

echo "=== Deploying Horror Theme + Hint System ==="

# 1. Copy login page
echo "Copying login.html..."
cp "$REPO_DIR/login.html" "$HTML_DIR/"

# 2. Copy finish page (horror styled)
echo "Copying finish.html..."
cp "$REPO_DIR/finish.html" "$HTML_DIR/"

# 2b. Copy highscore page (horror styled)
echo "Copying highscore.html..."
cp "$REPO_DIR/highscore.html" "$HTML_DIR/"

# 3. Copy Creepster font
echo "Copying Creepster font..."
cp "$REPO_DIR/Creepster-Regular.ttf" "$HTML_DIR/"

# 4. Copy clown image for flash effect
echo "Copying clown.jpg..."
cp "$REPO_DIR/clown.jpg" "$HTML_DIR/"

# 5. Copy theblackbox.html (main frame with hint button)
echo "Copying theblackbox.html..."
cp "$REPO_DIR/theblackbox.html" "$HTML_DIR/"

# 6. Also update the copy in /opt/theblackbox/html/ if it exists
if [ -d "/opt/theblackbox/html" ]; then
    echo "Also updating /opt/theblackbox/html/..."
    cp "$REPO_DIR/login.html" "/opt/theblackbox/html/"
    cp "$REPO_DIR/finish.html" "/opt/theblackbox/html/"
    cp "$REPO_DIR/highscore.html" "/opt/theblackbox/html/"
    cp "$REPO_DIR/theblackbox.html" "/opt/theblackbox/html/"
    cp "$REPO_DIR/Creepster-Regular.ttf" "/opt/theblackbox/html/"
    cp "$REPO_DIR/clown.jpg" "/opt/theblackbox/html/"
fi

# 7. Run hint system patch on server code
echo ""
echo "=== Patching server for hint system ==="
python3 "$REPO_DIR/add_hint_system.py"

echo ""
echo "=== Done! ==="
echo "Now restart the server: sudo bash /opt/theblackbox/restart.sh"
echo ""
echo "Don't forget to add hints to theblackbox.ini per challenge:"
echo "  [Challenge1]"
echo "  hint1 = Your first hint text"
echo "  hint2 = Your second hint text"
echo "  hint3 = Your third hint text"
