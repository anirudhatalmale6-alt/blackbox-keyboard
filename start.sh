#!/bin/bash
export DISPLAY=:0
export XAUTHORITY=/home/pi/.Xauthority

# Clear LCD on startup
sleep 3 && sudo python3 /opt/theblackbox/lcd_clear.py

# Kill any existing Firefox processes to prevent port 2828 conflict
pkill -9 -f firefox-esr 2>/dev/null || true
pkill -9 -f firefox 2>/dev/null || true
sleep 2

# Clean Firefox lock files to prevent 'already running' error
rm -f /home/pi/.mozilla/firefox/*/lock
rm -f /home/pi/.mozilla/firefox/*/.parentlock

# Clear Firefox crash data and session restore (prevents AsyncShutdown hang)
rm -rf /home/pi/.mozilla/firefox/*/minidumps/*
rm -f /home/pi/.mozilla/firefox/*/sessionstore*
rm -f /home/pi/.mozilla/firefox/*/sessionCheckpoints.json

# Clear Firefox cache
rm -rf /home/pi/.cache/mozilla/firefox/*/cache2
rm -rf /home/pi/.mozilla/firefox/*/cache2

# Wait for port 2828 to be free
for i in $(seq 1 10); do
    if ! ss -tlnp 2>/dev/null | grep -q ":2828 "; then
        break
    fi
    echo "Port 2828 still in use, waiting... ($i)"
    sleep 2
done

# Start Firefox in kiosk mode
firefox-esr --marionette --remote-allow-system-access --kiosk http://localhost/theblackbox/theblackbox.html &

# Wait for Marionette to be ready (port 2828)
echo "Waiting for Firefox Marionette..."
for i in {1..60}; do
if nc -z localhost 2828 2>/dev/null; then
echo "Marionette ready after $i seconds"
break
fi
sleep 1
done

# Start TheBlackBox (it will control the browser)
cd /opt/theblackbox
sudo DISPLAY=:0 /usr/bin/python3 /opt/theblackbox/theblackbox.py -d >> /tmp/theblackbox.log 2>&1 &

# Wait for API to be ready
echo "Waiting for BlackBox API..."
for i in {1..30}; do
if curl -s http://localhost:5000/banner > /dev/null 2>&1; then
echo "API ready after $i seconds"
break
fi
sleep 1
done

# Wait for browser connection and page load (check log for "Setting initial page")
echo "Waiting for page load..."
for i in {1..30}; do
if grep -q "Setting initial page" /tmp/theblackbox.log 2>/dev/null; then
echo "Page set after $i seconds"
break
fi
sleep 1
done

# Extra buffer for Firefox to render
sleep 15

# NOW hide Plymouth
plymouth --quit 2>/dev/null

echo "Startup complete"

# Keep script running - wait for Python process

# Start audio stream after everything is up
(sleep 20 && sudo systemctl start blackbox-audio) &
wait
