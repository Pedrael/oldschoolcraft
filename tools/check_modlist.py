#!/usr/bin/env python3
"""Compare a repo mod list against an installed mods folder to find mismatches.

Usage:
    check_modlist.py MODLIST_FILE MODS_DIR

MODLIST_FILE is a tab-separated "index<TAB>filename.jar" listing (as found
under game/client/modlist.txt, game/server/modlist.txt, etc). MODS_DIR is a
local Minecraft mods folder containing the actual .jar files.

Reports mods present in the list but missing from the folder, and jars
present in the folder but absent from the list.
"""

import argparse
import sys
from pathlib import Path


def parse_modlist(modlist_path: Path) -> set[str]:
    names = set()
    for lineno, line in enumerate(modlist_path.read_text().splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        name = parts[-1].strip()
        if not name:
            print(f"warning: {modlist_path}:{lineno}: could not parse entry, skipping", file=sys.stderr)
            continue
        names.add(name)
    return names


def find_installed_jars(mods_dir: Path) -> set[str]:
    names = set()
    for pattern in ("*.jar", "*.zip"):
        names.update(p.name for p in mods_dir.glob(pattern))
    return names


def main() -> int:
    parser = argparse.ArgumentParser(description="Find mismatches between a repo mod list and an installed mods folder.")
    parser.add_argument("modlist", type=Path, help="Path to the repo modlist file (index<TAB>filename.jar per line)")
    parser.add_argument("mods_dir", type=Path, help="Path to the local Minecraft mods folder")
    args = parser.parse_args()

    if not args.modlist.is_file():
        parser.error(f"{args.modlist} is not a file")
    if not args.mods_dir.is_dir():
        parser.error(f"{args.mods_dir} is not a directory")

    listed = parse_modlist(args.modlist)
    installed = find_installed_jars(args.mods_dir)

    missing = sorted(listed - installed)
    extra = sorted(installed - listed)

    if missing:
        print(f"Missing from {args.mods_dir} ({len(missing)}):")
        for name in missing:
            print(f"  {name}")

    if extra:
        if missing:
            print()
        print(f"Not in {args.modlist} ({len(extra)}):")
        for name in extra:
            print(f"  {name}")

    if not missing and not extra:
        print("No mismatches found.")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
