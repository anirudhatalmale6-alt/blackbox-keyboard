#!/usr/bin/env python3
"""
Fix LCD init sequence in lcd_screen.py (v2 - minimal change only)

The HD44780 init requires the first 4 commands to be sent as SINGLE
4-bit nibbles. The original code uses _lcd_write_cmd() which sends
TWO nibbles per call, causing an extra 0x00 nibble before each command.

This fix ONLY changes the init nibbles. No other changes.
"""

filepath = '/opt/theblackbox/lcd_screen.py'

with open(filepath, 'r') as f:
    content = f.read()

old_init = """            # Initialisation routine
            self._lcd_write_cmd(0x03)
            self._lcd_write_cmd(0x03)
            self._lcd_write_cmd(0x03)
            self._lcd_write_cmd(0x02)"""

new_init = """            # Initialisation routine (single nibble writes for 4-bit mode switch)
            self._lcd_write_four_bits(0x30)
            self._lcd_write_four_bits(0x30)
            self._lcd_write_four_bits(0x30)
            self._lcd_write_four_bits(0x20)"""

if old_init in content:
    content = content.replace(old_init, new_init)
    with open(filepath, 'w') as f:
        f.write(content)
    print("OK - Fixed LCD init sequence (v2 - minimal)")
elif "self._lcd_write_four_bits(0x30)" in content:
    print("Already fixed!")
else:
    print("WARNING: Unexpected state in lcd_screen.py")
    # Show what's there
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'Initialisation' in line or 'write_cmd(0x03)' in line or 'write_four_bits(0x30)' in line:
            for j in range(max(0,i-1), min(i+6, len(lines))):
                print(f"  {j+1}: {lines[j]}")
            break
