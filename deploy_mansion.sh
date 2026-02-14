#!/bin/bash
# Deploy mansion challenge + GPIO service
# Run this on the Pi: sudo bash deploy_mansion.sh

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
HTML_DIR="/var/www/html/theblackbox"
BB_DIR="/opt/theblackbox"

echo "=== Deploying Mansion Challenge ==="

# 1. Copy challenge HTML and images to web directory
echo "Copying mansion files to $HTML_DIR..."
cp "$REPO_DIR/mansion_challenge.html" "$HTML_DIR/"
cp "$REPO_DIR/mansion_off.jpg" "$HTML_DIR/"
cp "$REPO_DIR/mansion_on_fixed.jpg" "$HTML_DIR/"

# 2. Deploy GPIO service
echo "Deploying GPIO service..."
cp "$REPO_DIR/gpio_service.py" "$BB_DIR/"

# 3. Install and start GPIO systemd service
echo "Installing GPIO systemd service..."
cp "$REPO_DIR/blackbox-gpio.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable blackbox-gpio.service
systemctl restart blackbox-gpio.service

# 4. Wait and verify
sleep 2
if systemctl is-active --quiet blackbox-gpio.service; then
    echo "GPIO service is running!"
else
    echo "WARNING: GPIO service failed to start. Check: journalctl -u blackbox-gpio.service"
fi

# 5. Test GPIO endpoint
if curl -s http://127.0.0.1:5001/gpio/set?pin=17\&state=0 > /dev/null 2>&1; then
    echo "GPIO endpoint responding OK!"
else
    echo "WARNING: GPIO endpoint not responding yet (may need a moment)"
fi

echo ""
echo "=== Done! ==="
echo "Now add mansion_challenge.html as a challenge in theblackbox.ini"
echo "Example: under [Challenge7] add:"
echo "  challenge_html = mansion_challenge.html"
echo "  challenge_sensors ="
echo ""
echo "Then restart: sudo systemctl restart theblackbox"
