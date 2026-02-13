#!/usr/bin/env python3
"""
Fix LCD initialization sequence in lcd_screen.py

The HD44780 init protocol requires the first 4 commands (0x03, 0x03, 0x03, 0x02)
to be sent as single 4-bit nibbles using _lcd_write_four_bits(), NOT as full
8-bit commands using _lcd_write_cmd().

_lcd_write_cmd(0x03) incorrectly sends two nibbles: 0x00 then 0x30
_lcd_write_four_bits(0x30) correctly sends just one nibble: 0x30

This causes garbled LCD output on boot because the LCD gets confused by
the extra 0x00 nibbles during initialization.
"""

filepath = '/opt/theblackbox/lcd_screen.py'

with open(filepath, 'r') as f:
    content = f.read()

old_init = """            # Initialisation routine
            self._lcd_write_cmd(0x03)
            self._lcd_write_cmd(0x03)
            self._lcd_write_cmd(0x03)
            self._lcd_write_cmd(0x02)"""

new_init = """            # Initialisation routine
            # These must be single 4-bit writes (not full 8-bit commands)
            # to properly switch LCD from 8-bit to 4-bit mode
            self._lcd_write_four_bits(0x30)
            self._lcd_write_four_bits(0x30)
            self._lcd_write_four_bits(0x30)
            self._lcd_write_four_bits(0x20)"""

if old_init in content:
    content = content.replace(old_init, new_init)
    with open(filepath, 'w') as f:
        f.write(content)
    print("OK - Fixed LCD init sequence!")
    print("Changed _lcd_write_cmd() to _lcd_write_four_bits() for init commands.")
    print("Restart needed: sudo bash /opt/theblackbox/restart.sh")
elif "self._lcd_write_four_bits(0x30)" in content:
    print("Already fixed!")
else:
    print("WARNING: Could not find the exact init block.")
    print("Check /opt/theblackbox/lcd_screen.py manually.")
