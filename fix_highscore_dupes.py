#!/usr/bin/env python3
"""
Fix duplicate entries in highscore list.
Changes the /player/list?highscore=1 endpoint to return all completed
players sorted by elapsed_time without the top15/bottom5 split that
causes duplicates when there are fewer than 20 players.
"""
import re

filepath = '/opt/theblackbox/theblackbox.py'

with open(filepath, 'r') as f:
    content = f.read()

# Find the old highscore block that splits top 15 / bottom 5
old_block = '''        if highscore > 0:
            # Get a list of players
            player_list = self._db_store_alt.list_players(flags_include=Player.FLAGS_CHALLENGE_COMPLETE, order_by="elapsed_time")
            # Get the top 15 players
            player_list_top = {k: player_list[k] for k in list(player_list)[:15]}
            # Get the bottom 5 players
            player_list_bottom = {k: player_list[k] for k in list(player_list)[-5:]}

            player_list_user = None
            # Check for uid in player lists (if specified)
            if uid >= 0 and not uid in player_list_top and not uid in player_list_bottom:
                player_list_user = player_list[uid]

            # Transform that in to JSON data
            # Top players
            for tmp_player in player_list_top.values():
                player_details.append({
                                       'uid': tmp_player.get_uid(),
                                       'player_name': tmp_player.get_player_name(),
                                       'elapsed_time': tmp_player.get_elapsed_time(),
                                       'elapsed_time_str': tmp_player.get_elapsed_time_str(),
                                       'rank': tmp_player.get_rank(),
                                      })
            # Player (if exists)
            if not player_list_user is None:
                player_details.append({
                                       'uid': player_list_user.get_uid(),
                                       'player_name': player_list_user.get_player_name(),
                                       'elapsed_time': player_list_user.get_elapsed_time(),
                                       'elapsed_time_str': player_list_user.get_elapsed_time_str(),
                                       'rank': player_list_user.get_rank(),
                                      })
            # Bottom players
            for tmp_player in player_list_bottom.values():
                player_details.append({
                                       'uid': tmp_player.get_uid(),
                                       'player_name': tmp_player.get_player_name(),
                                       'elapsed_time': tmp_player.get_elapsed_time(),
                                       'elapsed_time_str': tmp_player.get_elapsed_time_str(),
                                       'rank': tmp_player.get_rank(),
                                      })'''

new_block = '''        if highscore > 0:
            # Get all completed players sorted by time
            player_list = self._db_store_alt.list_players(flags_include=Player.FLAGS_CHALLENGE_COMPLETE, order_by="elapsed_time")

            # Transform into JSON data
            for tmp_player in player_list.values():
                player_details.append({
                                       'uid': tmp_player.get_uid(),
                                       'player_name': tmp_player.get_player_name(),
                                       'elapsed_time': tmp_player.get_elapsed_time(),
                                       'elapsed_time_str': tmp_player.get_elapsed_time_str(),
                                       'rank': tmp_player.get_rank(),
                                      })'''

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(filepath, 'w') as f:
        f.write(content)
    print("OK - Fixed! Removed top15/bottom5 split, now shows all completed players.")
    print("Restart needed: sudo bash /opt/theblackbox/restart.sh")
else:
    print("WARNING: Could not find the exact code block to replace.")
    print("Trying alternative approach...")

    # Check if already fixed
    if "# Get all completed players sorted by time" in content:
        print("Already fixed!")
    else:
        print("Code has been modified. Please check manually.")
        print("The fix is: in _rest_player_list, remove the top15/bottom5 split")
        print("and just return all players from player_list directly.")
