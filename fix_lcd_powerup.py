#!/usr/bin/env python3
"""
Fix LCD power-on timing in lcd_screen.py

The HD44780 datasheet requires waiting >40ms after power-on before
sending any commands. Without this delay, the init sequence may fail
intermittently (LCD sometimes empty, sometimes works).

This adds a 50ms delay before the init sequence starts.
"""

filepath = '/opt/theblackbox/lcd_screen.py'

with open(filepath, 'r') as f:
    content = f.read()

old_block = """            # Initialisation routine
            # These must be single 4-bit writes (not full 8-bit commands)
            # to properly switch LCD from 8-bit to 4-bit mode
            self._lcd_write_four_bits(0x30)"""

new_block = """            # Wait for LCD power-on (HD44780 needs >40ms after Vcc stable)
            sleep(0.05)

            # Initialisation routine
            # These must be single 4-bit writes (not full 8-bit commands)
            # to properly switch LCD from 8-bit to 4-bit mode
            self._lcd_write_four_bits(0x30)"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(filepath, 'w') as f:
        f.write(content)
    print("OK - Added 50ms power-on delay before LCD init!")
    print("Restart needed: sudo bash /opt/theblackbox/restart.sh")
elif "Wait for LCD power-on" in content:
    print("Already fixed!")
else:
    print("WARNING: Could not find init block. Current lcd_screen.py init:")
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '_lcd_write_four_bits(0x30)' in line:
            start = max(0, i-3)
            for j in range(start, min(i+8, len(lines))):
                print(f"  {j+1}: {lines[j]}")
            break
