#!/usr/bin/env python3
"""
Revert lcd_screen.py init and clear to original code.

The original code worked most of the time. Our changes made it worse.
This reverts ALL lcd_screen.py changes back to the original.
"""

filepath = '/opt/theblackbox/lcd_screen.py'

with open(filepath, 'r') as f:
    content = f.read()

changes_made = False

# Revert init sequence: remove power-on delay if present
if "# Wait for LCD power-on" in content:
    content = content.replace(
        """            # Wait for LCD power-on (HD44780 needs >40ms after Vcc stable)
            sleep(0.05)

            # Initialisation routine""",
        "            # Initialisation routine"
    )
    changes_made = True

# Revert init nibbles back to original _lcd_write_cmd calls
old_init_fixed = """            # Initialisation routine
            # These must be single 4-bit writes (not full 8-bit commands)
            # to properly switch LCD from 8-bit to 4-bit mode
            self._lcd_write_four_bits(0x30)
            sleep(0.005)  # HD44780 requires >4.1ms after first init
            self._lcd_write_four_bits(0x30)
            sleep(0.005)  # HD44780 requires >100us after second init
            self._lcd_write_four_bits(0x30)
            sleep(0.001)
            self._lcd_write_four_bits(0x20)
            sleep(0.001)"""

original_init = """            # Initialisation routine
            self._lcd_write_cmd(0x03)
            self._lcd_write_cmd(0x03)
            self._lcd_write_cmd(0x03)
            self._lcd_write_cmd(0x02)"""

if old_init_fixed in content:
    content = content.replace(old_init_fixed, original_init)
    changes_made = True

# Revert clear() timing delays
old_clear = """            self._lcd_write_cmd(LcdScreen.CMD_CLEARDISPLAY)
            sleep(0.002)  # HD44780 clear takes 1.52ms
            self._lcd_write_cmd(LcdScreen.CMD_RETURNHOME)
            sleep(0.002)  # HD44780 return home takes 1.52ms"""

original_clear = """            self._lcd_write_cmd(LcdScreen.CMD_CLEARDISPLAY)
            self._lcd_write_cmd(LcdScreen.CMD_RETURNHOME)"""

if old_clear in content:
    content = content.replace(old_clear, original_clear)
    changes_made = True

if changes_made:
    with open(filepath, 'w') as f:
        f.write(content)
    print("OK - Reverted lcd_screen.py to original code!")
    print("Restart needed: sudo bash /opt/theblackbox/restart.sh")
else:
    # Check if already original
    if "self._lcd_write_cmd(0x03)" in content and "sleep(0.002)" not in content:
        print("Already at original code!")
    else:
        print("WARNING: Unexpected state. Current init section:")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'Initialisation routine' in line:
                for j in range(i, min(i+15, len(lines))):
                    print(f"  {j+1}: {lines[j]}")
                break
