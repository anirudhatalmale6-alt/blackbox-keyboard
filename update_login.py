#!/usr/bin/env python3
"""
Download updated login.html from GitHub and deploy it.
Also clears Firefox cache so the change takes effect.
"""
import subprocess
import os
import shutil

URL = "https://raw.githubusercontent.com/anirudhatalmale6-alt/blackbox-keyboard/master/login.html"
TARGET = "/var/www/html/theblackbox/login.html"
BACKUP = "/tmp/login.html.bak"

print("1. Backing up current login.html...")
if os.path.exists(TARGET):
    shutil.copy2(TARGET, BACKUP)
    print(f"   Backup saved to {BACKUP}")

print("2. Downloading new login.html...")
result = subprocess.run(["wget", "-q", "-O", TARGET, URL], capture_output=True, text=True)
if result.returncode != 0:
    print(f"   ERROR: Download failed: {result.stderr}")
    exit(1)
print("   Download complete!")

print("3. Clearing Firefox cache...")
import glob
for pattern in ["/home/pi/.cache/mozilla/firefox/*/cache2", "/home/pi/.mozilla/firefox/*/cache2"]:
    for path in glob.glob(pattern):
        if os.path.isdir(path):
            shutil.rmtree(path)
            print(f"   Removed {path}")
print("   Cache cleared!")

print("4. Restarting TheBlackBox...")
subprocess.run(["sudo", "bash", "/opt/theblackbox/restart.sh"], capture_output=True)
print("   Restart initiated!")

print()
print("Done! The login page should now show a preview bar above the keyboard")
print("showing the field name and what you're typing.")
