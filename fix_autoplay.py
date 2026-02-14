#!/usr/bin/env python3
"""
Enable audio autoplay in Firefox by setting media.autoplay.default = 0

This allows soundofsilence.mp3 to play automatically on the login page
without requiring user interaction first.
"""

filepath = '/opt/theblackbox/browser.py'

with open(filepath, 'r') as f:
    content = f.read()

if 'media.autoplay.default' in content:
    print("Already fixed!")
else:
    old = '        # Allow video playback fullscreen\n        self._firefox.set_pref_bool("full-screen-api.allow-trusted-requests-only", False)'
    new = '        # Allow video playback fullscreen\n        self._firefox.set_pref_bool("full-screen-api.allow-trusted-requests-only", False)\n\n        # Allow audio/video autoplay without user interaction\n        self._firefox.set_pref("media.autoplay.default", 0)'

    if old in content:
        content = content.replace(old, new)
        with open(filepath, 'w') as f:
            f.write(content)
        print("OK - Enabled audio autoplay in Firefox!")
        print("Restart needed: sudo bash /opt/theblackbox/restart.sh")
    else:
        print("WARNING: Could not find the expected code block.")
        print("Please check browser.py manually.")
