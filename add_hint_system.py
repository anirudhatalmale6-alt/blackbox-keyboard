#!/usr/bin/env python3
"""
Patch script: Add hint system to The BlackBox escape room.

Patches three files on the Raspberry Pi:
  1. challenge.py  - Add hints parameter, get_hints(), get_hint(index)
  2. config.py     - Load hint1/hint2/hint3 from ini, pass to Challenge
  3. theblackbox.py - Add _hints_used tracking, /challenge/hint route, handler

Hint behaviour:
  - Each challenge can have up to 3 optional hints (hint1, hint2, hint3 in ini)
  - Requesting a hint adds a 1200-second (20-minute) penalty to elapsed_time
  - Hints are tracked per challenge index so each challenge has its own counter
  - Already-applied patches are detected and skipped

Usage on the Pi:
  python3 add_hint_system.py
  sudo bash /opt/theblackbox/restart.sh
"""

import os
import sys

# ---------------------------------------------------------------------------
# File paths on the Pi
# ---------------------------------------------------------------------------
CHALLENGE_PY = "/opt/theblackbox/challenge.py"
CONFIG_PY = "/opt/theblackbox/config.py"
THEBLACKBOX_PY = "/opt/theblackbox/theblackbox.py"

HINT_PENALTY_SECONDS = 1200  # 20 minutes

errors = []
patched = []
skipped = []


def read_file(path):
    """Read a file and return its contents, or None on failure."""
    if not os.path.exists(path):
        errors.append(f"File not found: {path}")
        return None
    with open(path, "r") as f:
        return f.read()


def write_file(path, content):
    """Write content to a file."""
    with open(path, "w") as f:
        f.write(content)


# ===========================================================================
# 1. Patch challenge.py
# ===========================================================================
def patch_challenge():
    content = read_file(CHALLENGE_PY)
    if content is None:
        return

    # --- Already patched? ---
    if "get_hints" in content and "self._hints" in content:
        skipped.append(f"{CHALLENGE_PY} (hint system already present)")
        return

    # --- Patch __init__ signature and body ---
    old_init = (
        "def __init__(self, page, sensors):\n"
        "        self._page = page\n"
        "        self._sensors = sensors"
    )
    new_init = (
        "def __init__(self, page, sensors, hints=None):\n"
        "        self._page = page\n"
        "        self._sensors = sensors\n"
        "        self._hints = hints if hints is not None else []"
    )

    if old_init not in content:
        # Try to match if already partially patched or indentation differs
        errors.append(
            f"{CHALLENGE_PY}: Could not find expected __init__ block. "
            "Please check the file manually."
        )
        return

    content = content.replace(old_init, new_init)

    # --- Add get_hints() and get_hint(index) methods ---
    # Insert after get_sensors method
    old_get_sensors = (
        "    def get_sensors(self):\n"
        "        return self._sensors"
    )
    new_get_sensors = (
        "    def get_sensors(self):\n"
        "        return self._sensors\n"
        "\n"
        "    def get_hints(self):\n"
        "        return self._hints\n"
        "\n"
        "    def get_hint(self, index):\n"
        "        if index < 0 or index >= len(self._hints):\n"
        "            return None\n"
        "        return self._hints[index]"
    )

    if old_get_sensors not in content:
        errors.append(
            f"{CHALLENGE_PY}: Could not find get_sensors() method. "
            "Please check the file manually."
        )
        return

    content = content.replace(old_get_sensors, new_get_sensors)
    write_file(CHALLENGE_PY, content)
    patched.append(CHALLENGE_PY)


# ===========================================================================
# 2. Patch config.py
# ===========================================================================
def patch_config():
    content = read_file(CONFIG_PY)
    if content is None:
        return

    # --- Already patched? ---
    if "tmp_hints" in content and 'hint1' in content:
        skipped.append(f"{CONFIG_PY} (hint loading already present)")
        return

    # Find the Challenge constructor call (indentation-agnostic)
    construct_marker = "tmp_challenge = Challenge(tmp_page, tmp_sensors)"
    if construct_marker not in content:
        if "Challenge(tmp_page, tmp_sensors, tmp_hints)" in content:
            skipped.append(f"{CONFIG_PY} (Challenge constructor already updated)")
            return
        errors.append(
            f"{CONFIG_PY}: Could not find 'tmp_challenge = Challenge(tmp_page, tmp_sensors)'. "
            "Please check the file manually."
        )
        return

    # Detect the indentation of the Challenge constructor line
    construct_idx = content.find(construct_marker)
    line_start = content.rfind("\n", 0, construct_idx) + 1
    construct_indent = content[line_start:construct_idx]  # leading whitespace

    # Build hint-loading code using the same indentation as the constructor line
    ind = construct_indent  # base indent (same level as tmp_challenge = ...)
    hint_loading_lines = [
        f"{ind}# Load optional hints for this challenge",
        f"{ind}tmp_hints = []",
        f"{ind}for hint_num in range(1, 4):",
        f'{ind}    hint_key = f"hint{{hint_num}}"',
        f"{ind}    if self._cfg.has_option(section_str, hint_key):",
        f"{ind}        hint_val = self._cfg.get(section_str, hint_key).strip()",
        f"{ind}        if hint_val:",
        f"{ind}            tmp_hints.append(hint_val)",
    ]
    hint_loading_code = "\n".join(hint_loading_lines) + "\n"

    # Find the full line including its indentation
    old_full_line = content[line_start:content.find("\n", construct_idx)]
    new_full_line = old_full_line.replace(
        "Challenge(tmp_page, tmp_sensors)",
        "Challenge(tmp_page, tmp_sensors, tmp_hints)",
    )

    # Replace: insert hint loading block before the constructor line,
    # and update the constructor call in one go
    content = content.replace(
        old_full_line,
        hint_loading_code + new_full_line,
    )

    write_file(CONFIG_PY, content)
    patched.append(CONFIG_PY)


# ===========================================================================
# 3. Patch theblackbox.py
# ===========================================================================
def patch_theblackbox():
    content = read_file(THEBLACKBOX_PY)
    if content is None:
        return

    changes_made = False

    # --- 3a. Add self._hints_used = {} in __init__ ---
    if "self._hints_used" not in content:
        # Insert after self._challenge_index = 0
        old_challenge_index = "self._challenge_index = 0"
        if old_challenge_index in content:
            content = content.replace(
                old_challenge_index,
                old_challenge_index + "\n        self._hints_used = {}",
            )
            changes_made = True
        else:
            errors.append(
                f"{THEBLACKBOX_PY}: Could not find 'self._challenge_index = 0' "
                "for _hints_used init. Please check the file manually."
            )
    else:
        skipped.append(f"{THEBLACKBOX_PY}: self._hints_used already present in __init__")

    # --- 3b. Reset self._hints_used = {{}} in _player_data_load ---
    # We look for the pattern where _challenge_index is set inside
    # _player_data_load.  It typically looks like:
    #   self._challenge_index = <something>
    # inside that method.  We need to add reset after it.
    # We search for the method and the assignment within it.

    if "_player_data_load" in content:
        # Find _player_data_load method
        method_start = content.find("def _player_data_load")
        if method_start != -1:
            # Find self._challenge_index assignment inside this method
            # (not the __init__ one we already modified)
            search_start = method_start
            idx = content.find("self._challenge_index", search_start)
            if idx != -1 and idx > method_start:
                # Find the end of this line
                line_end = content.find("\n", idx)
                if line_end != -1:
                    line = content[idx:line_end]
                    # Check if hints_used reset is already on the next line
                    next_lines = content[line_end:line_end + 100]
                    if "self._hints_used = {}" not in next_lines:
                        # Get the indentation of the current line
                        line_start = content.rfind("\n", method_start, idx) + 1
                        indent = ""
                        for ch in content[line_start:idx]:
                            if ch in (" ", "\t"):
                                indent += ch
                            else:
                                break
                        content = (
                            content[:line_end]
                            + "\n"
                            + indent
                            + "self._hints_used = {}"
                            + content[line_end:]
                        )
                        changes_made = True
                    else:
                        skipped.append(
                            f"{THEBLACKBOX_PY}: _hints_used reset already in _player_data_load"
                        )
            else:
                # _challenge_index not set in _player_data_load -- try alternate pattern
                # Some versions set it via a different attribute.  We'll add it after
                # the method def line + first assignment we find.
                errors.append(
                    f"{THEBLACKBOX_PY}: Could not find _challenge_index assignment "
                    "in _player_data_load. Please add 'self._hints_used = {{}}' manually."
                )
    else:
        errors.append(
            f"{THEBLACKBOX_PY}: Could not find _player_data_load method."
        )

    # --- 3c. Add /challenge/hint route ---
    route_line = 'self._rest_router.add_api_route("/challenge/hint"'
    if route_line not in content:
        # Insert after the /challenge/action route
        action_route = 'self._rest_router.add_api_route("/challenge/action", self._rest_challenge_action, methods=["GET"])'
        if action_route in content:
            hint_route = (
                '\n        self._rest_router.add_api_route("/challenge/hint", '
                'self._rest_challenge_hint, methods=["GET"])'
            )
            content = content.replace(action_route, action_route + hint_route)
            changes_made = True
        else:
            # Try a more relaxed match (in case of slight formatting differences)
            alt_action = '/challenge/action"'
            if alt_action in content:
                # Find the full line
                idx = content.find(alt_action)
                line_end = content.find("\n", idx)
                if line_end != -1:
                    # Get indentation
                    line_start = content.rfind("\n", 0, idx) + 1
                    indent = ""
                    for ch in content[line_start:]:
                        if ch in (" ", "\t"):
                            indent += ch
                        else:
                            break
                    hint_route = (
                        "\n"
                        + indent
                        + 'self._rest_router.add_api_route("/challenge/hint", '
                        + 'self._rest_challenge_hint, methods=["GET"])'
                    )
                    content = content[:line_end] + hint_route + content[line_end:]
                    changes_made = True
                else:
                    errors.append(
                        f"{THEBLACKBOX_PY}: Found /challenge/action route but could "
                        "not determine line end."
                    )
            else:
                errors.append(
                    f"{THEBLACKBOX_PY}: Could not find /challenge/action route to "
                    "insert /challenge/hint route after. Please add manually."
                )
    else:
        skipped.append(f"{THEBLACKBOX_PY}: /challenge/hint route already present")

    # --- 3d. Add _rest_challenge_hint method ---
    method_marker = "def _rest_challenge_hint"
    if method_marker not in content:
        # We insert the method after _rest_challenge_action method.
        # Find _rest_challenge_action and locate the next method def at the
        # same indentation level to insert before it.
        hint_method = '''
    # ---- Hint system ----
    def _rest_challenge_hint(self):
        """Return the next hint for the current challenge and apply a time penalty."""
        if self._player is None:
            return {"error": "no player logged in"}

        challenge_idx = self._challenge_index
        challenge = self._challenges[challenge_idx]
        hints = challenge.get_hints()

        if not hints:
            return {"error": "no hints available"}

        # How many hints have been used for this challenge so far?
        used = self._hints_used.get(challenge_idx, 0)

        if used >= len(hints):
            return {"error": "no more hints"}

        # Get the next hint
        hint_text = hints[used]
        used += 1
        self._hints_used[challenge_idx] = used

        # Apply time penalty (add ''' + str(HINT_PENALTY_SECONDS) + ''' seconds = ''' + str(HINT_PENALTY_SECONDS // 60) + ''' minutes)
        current_elapsed = self._player.get_elapsed_time()
        self._player.set_elapsed_time(current_elapsed + ''' + str(HINT_PENALTY_SECONDS) + ''')

        return {
            "hint": hint_text,
            "hint_number": used,
            "hints_total": len(hints),
            "penalty_minutes": ''' + str(HINT_PENALTY_SECONDS // 60) + '''
        }
'''

        # Find _rest_challenge_action to insert after it
        action_method_idx = content.find("def _rest_challenge_action")
        if action_method_idx != -1:
            # Find the next method definition at the same indentation level
            # (i.e., "    def " at the class level)
            search_from = action_method_idx + 1
            # Skip past the current method's def line
            next_line = content.find("\n", search_from)
            if next_line != -1:
                search_from = next_line + 1

            # Look for the next "    def " which signals the start of the
            # next method in the class
            next_method_idx = -1
            pos = search_from
            while pos < len(content):
                nl = content.find("\n", pos)
                if nl == -1:
                    break
                line = content[pos:nl]
                stripped = line.lstrip()
                # A new method at the same class level (4-space indent)
                if stripped.startswith("def ") and (
                    line.startswith("    def ") or line.startswith("\tdef ")
                ):
                    next_method_idx = pos
                    break
                # If we hit a class or top-level def, also stop
                if stripped.startswith("class ") or (
                    stripped.startswith("def ") and not line[0].isspace()
                ):
                    next_method_idx = pos
                    break
                pos = nl + 1

            if next_method_idx != -1:
                content = (
                    content[:next_method_idx]
                    + hint_method
                    + "\n"
                    + content[next_method_idx:]
                )
                changes_made = True
            else:
                # Append at end of file (before last newline if present)
                content = content.rstrip("\n") + "\n" + hint_method + "\n"
                changes_made = True
        else:
            # Fallback: append at end of file
            content = content.rstrip("\n") + "\n" + hint_method + "\n"
            changes_made = True
    else:
        skipped.append(f"{THEBLACKBOX_PY}: _rest_challenge_hint method already present")

    if changes_made:
        write_file(THEBLACKBOX_PY, content)
        patched.append(THEBLACKBOX_PY)


# ===========================================================================
# Main
# ===========================================================================
def main():
    print("=" * 60)
    print("  The BlackBox - Hint System Patch")
    print("=" * 60)
    print()

    patch_challenge()
    patch_config()
    patch_theblackbox()

    print()

    if patched:
        print("PATCHED successfully:")
        for p in patched:
            print(f"  + {p}")
        print()

    if skipped:
        print("SKIPPED (already applied):")
        for s in skipped:
            print(f"  ~ {s}")
        print()

    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  ! {e}")
        print()

    if not errors:
        print("All patches applied successfully.")
    else:
        print("Some patches had errors - please review above.")

    print()
    print("Restart needed: sudo bash /opt/theblackbox/restart.sh")
    print()
    print("INI configuration example (add to each [ChallengeN] section):")
    print('  hint1 = Check under the table')
    print('  hint2 = The code is related to the painting')
    print('  hint3 = Try 4-7-2-9')
    print()
    print("API usage:")
    print("  GET /challenge/hint")
    print("  Returns: {hint, hint_number, hints_total, penalty_minutes}")
    print("  Each hint adds a 20-minute penalty to the player's elapsed time.")
    print()


if __name__ == "__main__":
    main()
