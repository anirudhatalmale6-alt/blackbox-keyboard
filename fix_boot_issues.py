#!/usr/bin/env python3
"""
Fix two boot issues on The BlackBox:
1. Firefox 'already running' error - add lock file cleanup to start.sh
2. blackbox-audio service not starting - add audio start to start.sh as workaround
"""

import subprocess
import sys

def fix_start_sh():
    """Add Firefox lock cleanup and audio stream start to start.sh"""
    filepath = '/opt/theblackbox/start.sh'

    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"ERROR: {filepath} not found!")
        return False

    print(f"Current start.sh content:")
    print("=" * 60)
    print(content)
    print("=" * 60)

    modified = False

    # 1. Add Firefox lock file cleanup BEFORE Firefox starts
    # Look for the line that starts Firefox (firefox-esr or firefox)
    lock_cleanup = """# Clean Firefox lock files to prevent 'already running' error
rm -f /home/pi/.mozilla/firefox/*/lock
rm -f /home/pi/.mozilla/firefox/*/.parentlock
"""

    if '.parentlock' not in content:
        # Find where Firefox is launched and add cleanup before it
        lines = content.split('\n')
        new_lines = []
        added_lock_cleanup = False

        for line in lines:
            # Add lock cleanup before the first Firefox launch command
            if not added_lock_cleanup and ('firefox' in line.lower() and ('&' in line or 'esr' in line.lower()) and not line.strip().startswith('#')):
                # Add cleanup lines before Firefox launch
                for cleanup_line in lock_cleanup.strip().split('\n'):
                    new_lines.append(cleanup_line)
                new_lines.append('')
                added_lock_cleanup = True
                modified = True
                print(">> Added Firefox lock file cleanup before Firefox launch")
            new_lines.append(line)

        if not added_lock_cleanup:
            # If we couldn't find the Firefox launch line, add at the beginning after shebang
            print(">> Could not find Firefox launch line, adding lock cleanup after shebang")
            new_lines = []
            for i, line in enumerate(lines):
                new_lines.append(line)
                if i == 0 and line.startswith('#!'):
                    new_lines.append('')
                    for cleanup_line in lock_cleanup.strip().split('\n'):
                        new_lines.append(cleanup_line)
                    new_lines.append('')
                    modified = True
                    print(">> Added Firefox lock file cleanup after shebang")

        content = '\n'.join(new_lines)
    else:
        print(">> Lock file cleanup already present in start.sh")

    # 2. Add audio stream start at the end of the script
    audio_start = """
# Start audio stream after everything is up
(sleep 20 && sudo systemctl start blackbox-audio) &
"""

    if 'blackbox-audio' not in content:
        # Add before the final 'wait' command if it exists, or at the end
        if '\nwait' in content or content.strip().endswith('wait'):
            content = content.rstrip()
            # Find the last 'wait' and add before it
            lines = content.split('\n')
            new_lines = []
            added_audio = False
            # Go through lines in reverse to find last 'wait'
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip() == 'wait' and not added_audio:
                    # Insert audio start before this wait
                    lines.insert(i, audio_start.strip())
                    lines.insert(i, '')
                    added_audio = True
                    break
            content = '\n'.join(lines) + '\n'
        else:
            content = content.rstrip() + '\n' + audio_start
        modified = True
        print(">> Added blackbox-audio start to start.sh")
    else:
        print(">> blackbox-audio start already present in start.sh")

    if modified:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"\nstart.sh has been updated!")
        print(f"\nNew start.sh content:")
        print("=" * 60)
        with open(filepath, 'r') as f:
            print(f.read())
        print("=" * 60)
    else:
        print("\nNo changes needed to start.sh")

    return True


def fix_audio_service():
    """
    Fix the blackbox-audio systemd service to be more robust.
    Change After= to use multi-user.target instead of theblackbox.service
    """
    filepath = '/etc/systemd/system/blackbox-audio.service'

    new_service = """[Unit]
Description=BlackBox Audio Stream
After=network.target sound.target
Wants=icecast2.service

[Service]
Type=simple
User=pi
ExecStartPre=/bin/sleep 20
ExecStart=/opt/theblackbox/audio-stream.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

    try:
        with open(filepath, 'r') as f:
            old_content = f.read()
        print(f"Old service file:")
        print(old_content)
    except:
        print(f"Creating new service file")

    with open(filepath, 'w') as f:
        f.write(new_service)

    print(f"New service file written:")
    print(new_service)

    # Reload systemd
    subprocess.run(['systemctl', 'daemon-reload'], check=True)
    print("systemd daemon reloaded")

    # Re-enable the service
    subprocess.run(['systemctl', 'enable', 'blackbox-audio'], check=True)
    print("blackbox-audio service re-enabled")

    return True


if __name__ == '__main__':
    print("=" * 60)
    print("Fixing BlackBox boot issues")
    print("=" * 60)
    print()

    print("Step 1: Fixing start.sh (Firefox locks + audio start)")
    print("-" * 60)
    fix_start_sh()
    print()

    print("Step 2: Fixing blackbox-audio service file")
    print("-" * 60)
    fix_audio_service()
    print()

    print("=" * 60)
    print("All fixes applied!")
    print("Please reboot to test: sudo reboot")
    print("=" * 60)
