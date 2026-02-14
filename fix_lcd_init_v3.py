#!/usr/bin/env python3
"""
Fix LCD init sequence in lcd_screen.py (v3 - robust for both cold and warm boot)

The HD44780 needs different handling depending on whether it's
cold-starting (power was off = 8-bit mode) or warm-starting
(reboot only = still in 4-bit mode from before).

This fix:
1. Adds 50ms initial delay for LCD power stabilization (cold boot)
2. Uses single nibble writes (correct for 8-bit mode entry)
3. Adds proper inter-command delays per HD44780 datasheet
4. Adds 2ms delay after clear display command

ONLY modifies the __init__ and clear methods, nothing else.
"""

filepath = '/opt/theblackbox/lcd_screen.py'

with open(filepath, 'r') as f:
    lines = content = f.read()

changes = 0

# --- Fix 1: Init sequence ---
# Try current state (v2 fix applied)
old_init_v2 = """            # Initialisation routine (single nibble writes for 4-bit mode switch)
            self._lcd_write_four_bits(0x30)
            self._lcd_write_four_bits(0x30)
            self._lcd_write_four_bits(0x30)
            self._lcd_write_four_bits(0x20)"""

# Or original state
old_init_orig = """            # Initialisation routine
            self._lcd_write_cmd(0x03)
            self._lcd_write_cmd(0x03)
            self._lcd_write_cmd(0x03)
            self._lcd_write_cmd(0x02)"""

new_init = """            # Wait for LCD power stabilization (cold boot needs >40ms)
            sleep(0.05)

            # Initialisation routine - robust for both cold and warm boot
            # HD44780 datasheet: send 0x3 three times with delays, then 0x2
            self._lcd_write_four_bits(0x30)
            sleep(0.005)  # >4.1ms after first
            self._lcd_write_four_bits(0x30)
            sleep(0.005)  # >4.1ms after second
            self._lcd_write_four_bits(0x30)
            sleep(0.0002)  # >100us after third
            self._lcd_write_four_bits(0x20)
            sleep(0.0002)"""

if old_init_v2 in content:
    content = content.replace(old_init_v2, new_init)
    changes += 1
    print("Replaced v2 init with v3")
elif old_init_orig in content:
    content = content.replace(old_init_orig, new_init)
    changes += 1
    print("Replaced original init with v3")
elif "sleep(0.05)" in content and "_lcd_write_four_bits(0x30)" in content:
    print("Init already at v3")
else:
    print("WARNING: Could not find init block")

# --- Fix 2: Add delay after CLEARDISPLAY in clear() ---
old_clear = """            self._lcd_write_cmd(LcdScreen.CMD_CLEARDISPLAY)
            self._lcd_write_cmd(LcdScreen.CMD_RETURNHOME)"""

new_clear = """            self._lcd_write_cmd(LcdScreen.CMD_CLEARDISPLAY)
            sleep(0.003)  # clear display needs 1.52ms
            self._lcd_write_cmd(LcdScreen.CMD_RETURNHOME)
            sleep(0.003)  # return home needs 1.52ms"""

if old_clear in content:
    content = content.replace(old_clear, new_clear)
    changes += 1
    print("Added delays to clear()")
elif "sleep(0.003)  # clear display" in content:
    print("Clear delays already present")
else:
    print("WARNING: Could not find clear() block")

if changes > 0:
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"\nOK - Applied {changes} fix(es) to lcd_screen.py")
    print("Test with: sudo reboot")
else:
    print("\nNo changes needed")
