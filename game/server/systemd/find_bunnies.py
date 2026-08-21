#!/usr/bin/env python3
"""Find MoCreatures bunnies near a point, in the live world and in a backup.

Vera's bunnies were killed by a Kitty. She wants the SAME bunnies back, not
fresh ones with the same look - so we need their real NBT (UUID, type/colour,
name, age, health), which only survives in a backup taken while they lived.

Usage:
  find_bunnies.py <x> <z> [radius_chunks] [--backup <backup.zip>]
"""
import gzip, io, os, struct, sys, zlib, zipfile, json

sys.path.insert(0, "/home/duduserver/mctools")
import nbtread

SECTOR = 4096
ROOT = "/home/duduserver/minecraft/1.7.10"
WANT = "MoCreatures.Bunny"


def chunks_from_region(blob):
    """{index: chunk_nbt} from raw region-file bytes."""
    out = {}
    loc = blob[:SECTOR]
    for i in range(1024):
        off = struct.unpack(">I", b"\x00" + loc[i * 4:i * 4 + 3])[0]
        cnt = loc[i * 4 + 3]
        if not off or not cnt:
            continue
        base = off * SECTOR
        if base + 5 > len(blob):
            continue
        ln = struct.unpack(">I", blob[base:base + 4])[0]
        if ln <= 0:
            continue
        comp = blob[base + 4]
        data = blob[base + 5: base + 4 + ln]
        try:
            raw = zlib.decompress(data) if comp == 2 else gzip.decompress(data)
        except Exception:
            continue
        try:
            r = nbtread.Reader(raw)
            if r.u1() != 10:
                continue
            r.string()
            out[i] = r.payload(10)
        except Exception:
            continue
    return out


def region_bytes(rx, rz, backup=None):
    rel = f"world/region/r.{rx}.{rz}.mca"
    if backup is None:
        p = os.path.join(ROOT, rel)
        return open(p, "rb").read() if os.path.exists(p) else None
    with zipfile.ZipFile(backup) as z:
        for cand in (rel, "./" + rel, rel.replace("world/", "")):
            try:
                return z.read(cand)
            except KeyError:
                continue
        # some backups nest the world folder differently - search
        for n in z.namelist():
            if n.endswith(f"r.{rx}.{rz}.mca"):
                return z.read(n)
    return None


def bunnies(cx0, cz0, radius, backup=None):
    found = {}
    regions = {}
    for cx in range(cx0 - radius, cx0 + radius + 1):
        for cz in range(cz0 - radius, cz0 + radius + 1):
            rx, rz = cx >> 5, cz >> 5
            if (rx, rz) not in regions:
                b = region_bytes(rx, rz, backup)
                regions[(rx, rz)] = chunks_from_region(b) if b else {}
            idx = (cx & 31) + (cz & 31) * 32
            ch = regions[(rx, rz)].get(idx)
            if not ch:
                continue
            lvl = ch.get("Level", {})
            for e in lvl.get("Entities", []) or []:
                if e.get("id") != WANT:
                    continue
                uid = (e.get("UUIDMost"), e.get("UUIDLeast"))
                found[uid] = e
    return found


def describe(e):
    pos = e.get("Pos", [0, 0, 0])
    return {
        "uuid": f'{e.get("UUIDMost")}:{e.get("UUIDLeast")}',
        "x": round(pos[0], 1), "y": round(pos[1], 1), "z": round(pos[2], 1),
        "type": e.get("TypeInt", e.get("Type")),
        "name": e.get("Name") or e.get("CustomName") or "",
        "age": e.get("Age"), "health": e.get("Health"),
        "tamed": e.get("Tamed"), "owner": e.get("Owner", ""),
        "adult": e.get("Adult"),
    }


if __name__ == "__main__":
    x, z = float(sys.argv[1]), float(sys.argv[2])
    radius = int(sys.argv[3]) if len(sys.argv) > 3 and not sys.argv[3].startswith("-") else 4
    backup = None
    if "--backup" in sys.argv:
        backup = sys.argv[sys.argv.index("--backup") + 1]
    cx, cz = int(x) >> 4, int(z) >> 4
    print(f"centre chunk ({cx},{cz}), radius {radius} chunks"
          f"{' from ' + os.path.basename(os.path.dirname(backup)) if backup else ' (LIVE)'}")
    b = bunnies(cx, cz, radius, backup)
    print(f"  {WANT} found: {len(b)}")
    for uid, e in b.items():
        d = describe(e)
        print(f"    {d['uuid']}  x={d['x']} y={d['y']} z={d['z']}  "
              f"type={d['type']} age={d['age']} hp={d['health']} "
              f"tamed={d['tamed']} owner={d['owner']!r} name={d['name']!r}")
    json.dump({f"{k[0]}:{k[1]}": describe(v) for k, v in b.items()},
              open("/tmp/bunnies_%s.json" % ("backup" if backup else "live"), "w"), indent=1)
