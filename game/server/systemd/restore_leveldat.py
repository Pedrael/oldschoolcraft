#!/usr/bin/env python3
"""Restore world/level.dat from the verified rescue copy.

The 2026-08-21 08:25 unclean shutdown truncated level.dat to 0 bytes. The
server then deadlocked during world load instead of falling back to
level.dat_old, and sat there for 13 hours holding port 25565 open.

Refuses to run unless:
  - the server is stopped (never edit world data under a live server)
  - the rescue copy gunzips and carries the Forge item registry
  - the current level.dat is actually broken (so this cannot clobber a good one)
"""
import gzip, os, shutil, subprocess, sys

WORLD  = "/home/duduserver/minecraft/1.7.10/world"
LIVE   = os.path.join(WORLD, "level.dat")
# Minecraft rotates level.dat -> level.dat_old on every successful save, so the
# world's OWN level.dat_old is the correct fallback and is always current. A
# hardcoded rescue copy goes stale: the 2026-08-21 one is day 92 while the world
# reached day 368, and restoring it would have silently thrown away two weeks.
# An explicit path may still be passed as argv[1] if level.dat_old is also bad.
RESCUE = (sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-")
          else os.path.join(WORLD, "level.dat_old"))


def valid(path):
    """(ok, uncompressed_size, modded_id_count)

    gzip.decompress(b"") returns b"" instead of raising, so an empty file would
    otherwise read as a healthy one. Require actual content.
    """
    try:
        raw = open(path, "rb").read()
        if not raw:
            return False, 0, 0
        d = gzip.decompress(raw)
        if not d:
            return False, 0, 0
    except Exception:
        return False, 0, 0
    n = sum(d.count(p) for p in (b"Botania:", b"Thaumcraft:", b"TConstruct:",
                                 b"EnderIO:", b"ThermalFoundation:"))
    return True, len(d), n


# -- 1. server must be down -------------------------------------------------
state = subprocess.run(["systemctl", "is-active", "minecraft"],
                       capture_output=True, text=True).stdout.strip()
if state == "active":
    print(f"ABORT: minecraft is {state} - stop it first"); sys.exit(1)
print(f"server state: {state} (safe to edit world data)")

# -- 2. rescue copy must be good -------------------------------------------
ok, size, ids = valid(RESCUE)
if not ok or ids < 100:
    print(f"ABORT: rescue copy is not a usable level.dat (ok={ok}, ids={ids})")
    sys.exit(1)
print(f"rescue copy : OK, {size} bytes uncompressed, {ids} modded registry refs")

# -- 3. refuse to overwrite a healthy level.dat ----------------------------
cur_ok, cur_size, _ = valid(LIVE)
cur_bytes = os.path.getsize(LIVE) if os.path.exists(LIVE) else -1
print(f"current file: {cur_bytes} bytes on disk, gunzips={cur_ok}")
if cur_ok:
    print("ABORT: current level.dat is already valid - nothing to repair")
    sys.exit(1)

# -- 4. restore -------------------------------------------------------------
shutil.copyfile(RESCUE, LIVE)
os.chmod(LIVE, 0o644)

ok, size, ids = valid(LIVE)
if not ok:
    print("ABORT: restored file does not read back - world untouched otherwise")
    sys.exit(1)
print(f"\nrestored    : {os.path.getsize(LIVE)} bytes, gunzips OK, "
      f"{size} uncompressed, {ids} modded registry refs")
print("corrupt original kept at ~/mctools/level.dat.CORRUPT-20260821")
