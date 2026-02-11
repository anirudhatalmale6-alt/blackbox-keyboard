#!/usr/bin/env python3
"""
Fix duplicate highscore entries - flexible version.
Reads the file line by line and replaces the top15/bottom5 block.
"""

filepath = '/opt/theblackbox/theblackbox.py'

with open(filepath, 'r') as f:
    lines = f.readlines()

# Find line numbers for the key markers
start_line = None
end_line = None

for i, line in enumerate(lines):
    # Find "if highscore > 0:"
    if 'if highscore > 0:' in line and start_line is None:
        start_line = i
    # Find the end: "elif uid > 0:" which comes after the highscore block
    if start_line is not None and 'elif uid > 0:' in line:
        end_line = i
        break

if start_line is None or end_line is None:
    print("ERROR: Could not find the highscore block boundaries")
    print(f"start_line={start_line}, end_line={end_line}")
    exit(1)

print(f"Found highscore block: lines {start_line+1} to {end_line}")
print(f"Old code ({end_line - start_line} lines):")
for i in range(start_line, end_line):
    print(f"  {i+1}: {lines[i].rstrip()}")

# Detect indentation from the start line
indent = ''
for ch in lines[start_line]:
    if ch in (' ', '\t'):
        indent += ch
    else:
        break

# Build replacement block
new_block = [
    f"{indent}if highscore > 0:\n",
    f"{indent}    # Get all completed players sorted by time\n",
    f"{indent}    player_list = self._db_store_alt.list_players(flags_include=Player.FLAGS_CHALLENGE_COMPLETE, order_by=\"elapsed_time\")\n",
    f"\n",
    f"{indent}    # Transform into JSON data\n",
    f"{indent}    for tmp_player in player_list.values():\n",
    f"{indent}        player_details.append({{\n",
    f"{indent}                               'uid': tmp_player.get_uid(),\n",
    f"{indent}                               'player_name': tmp_player.get_player_name(),\n",
    f"{indent}                               'elapsed_time': tmp_player.get_elapsed_time(),\n",
    f"{indent}                               'elapsed_time_str': tmp_player.get_elapsed_time_str(),\n",
    f"{indent}                               'rank': tmp_player.get_rank(),\n",
    f"{indent}                              }})\n",
]

# Replace the block
new_lines = lines[:start_line] + new_block + lines[end_line:]

with open(filepath, 'w') as f:
    f.writelines(new_lines)

print(f"\nOK - Fixed! Replaced {end_line - start_line} lines with {len(new_block)} lines.")
print("Now restart: sudo bash /opt/theblackbox/restart.sh")
