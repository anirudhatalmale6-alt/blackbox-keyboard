#!/usr/bin/env python3
"""
Fix LCD timing in lcd_screen.py

The HD44780 clear display and return home commands take 1.52ms to execute,
but the code only waits ~0.6ms between commands. This causes characters
to be lost or garbled because the LCD is still busy processing.

This fix adds a sleep(0.002) after clear display and return home commands
in the clear() method.
"""

filepath = '/opt/theblackbox/lcd_screen.py'

with open(filepath, 'r') as f:
    content = f.read()

# Fix 1: Add delay after clear() commands
old_clear = """    def clear(self):
        ''' Clear screen '''
        # Clear debug screen, if available
        if not self._fifo is None:
            # Send terminal clear screen
            os.write(self._fifo, "\\033c".encode())

        # Clear LCD, if available
        if not self._pcf8574 is None:
            self._lcd_write_cmd(LcdScreen.CMD_CLEARDISPLAY)
            self._lcd_write_cmd(LcdScreen.CMD_RETURNHOME)"""

new_clear = """    def clear(self):
        ''' Clear screen '''
        # Clear debug screen, if available
        if not self._fifo is None:
            # Send terminal clear screen
            os.write(self._fifo, "\\033c".encode())

        # Clear LCD, if available
        if not self._pcf8574 is None:
            self._lcd_write_cmd(LcdScreen.CMD_CLEARDISPLAY)
            sleep(0.002)  # HD44780 clear takes 1.52ms
            self._lcd_write_cmd(LcdScreen.CMD_RETURNHOME)
            sleep(0.002)  # HD44780 return home takes 1.52ms"""

if old_clear in content:
    content = content.replace(old_clear, new_clear)
    with open(filepath, 'w') as f:
        f.write(content)
    print("OK - Added timing delays to clear() method!")
    print("Restart needed: sudo bash /opt/theblackbox/restart.sh")
elif "sleep(0.002)  # HD44780 clear" in content:
    print("Already fixed!")
else:
    print("WARNING: Could not find the exact clear() block.")
    print("Showing clear method from file:")
    # Try to find and show the clear method
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'def clear(self)' in line:
            for j in range(i, min(i+15, len(lines))):
                print(f"  {j+1}: {lines[j]}")
            break
