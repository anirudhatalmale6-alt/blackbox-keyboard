#!/usr/bin/env python3
"""
Fix start.sh to properly kill old Firefox before starting.

The Firefox crash ("AsyncShutdown timeout") and Marionette "Could not bind
to port 2828" are caused by an old Firefox process still running when the
new one starts.

This script patches start.sh to:
1. Kill ALL Firefox processes before starting a new one
2. Wait for port 2828 to be free
3. Clear Firefox crash data that causes shutdown hangs
"""

filepath = '/opt/theblackbox/start.sh'

with open(filepath, 'r') as f:
    content = f.read()

# We need to see the current content to craft the right fix
# First, let's print what's there
print("=== Current start.sh ===")
print(content)
print("========================")

# Build the improved cleanup block that should go right before Firefox starts
cleanup_block = """# Kill any existing Firefox processes to prevent port 2828 conflict
pkill -9 -f firefox || true
sleep 2

# Clean Firefox lock files to prevent 'already running' error
rm -f /home/pi/.mozilla/firefox/*/lock
rm -f /home/pi/.mozilla/firefox/*/.parentlock

# Clear Firefox crash data and session restore (causes AsyncShutdown hangs)
rm -rf /home/pi/.mozilla/firefox/*/minidumps/*
rm -rf /home/pi/.mozilla/firefox/*/sessionstore*
rm -rf /home/pi/.mozilla/firefox/*/sessionCheckpoints.json

# Clear Firefox cache
rm -rf /home/pi/.cache/mozilla/firefox/*/cache2
rm -rf /home/pi/.mozilla/firefox/*/cache2

# Wait for port 2828 to be free
for i in $(seq 1 10); do
    if ! ss -tlnp | grep -q ":2828 "; then
        break
    fi
    echo "Port 2828 still in use, waiting... ($i)"
    sleep 2
done"""

# Check if pkill firefox is already in there
if 'pkill' in content and 'firefox' in content:
    print("\nstart.sh already has some Firefox kill logic.")
    print("Please share the current start.sh so I can update it properly:")
    print("  cat /opt/theblackbox/start.sh")
else:
    # Try to insert before the Firefox start line
    # Look for common patterns
    lines = content.split('\n')
    new_lines = []
    inserted = False

    for i, line in enumerate(lines):
        # Find where Firefox is started (firefox-esr or firefox with --kiosk or --marionette)
        stripped = line.strip()
        if not inserted and ('firefox' in stripped.lower() and
            ('kiosk' in stripped or 'marionette' in stripped or 'firefox-esr' in stripped) and
            not stripped.startswith('#')):
            # Insert cleanup block before Firefox launch
            # First remove any existing lock file cleanup lines that came before
            # (we'll include them in our block)
            while new_lines and ('rm -f /home/pi/.mozilla' in new_lines[-1] or
                                  new_lines[-1].strip() == ''):
                new_lines.pop()
            new_lines.append('')
            new_lines.append(cleanup_block)
            new_lines.append('')
            inserted = True

        new_lines.append(line)

    if inserted:
        new_content = '\n'.join(new_lines)
        with open(filepath, 'w') as f:
            f.write(new_content)
        print("\nOK - Patched start.sh with Firefox cleanup!")
        print("Restart needed: sudo reboot")
    else:
        print("\nCould not find Firefox launch line in start.sh.")
        print("Please share the content:")
        print("  cat /opt/theblackbox/start.sh")
