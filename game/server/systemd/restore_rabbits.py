#!/usr/bin/env python3
"""Restore ANY rabbit-like mob present in a backup and missing from the world.

This pack has two unrelated rabbit species and the first pass only looked at
one of them:

  MoCreatures.Bunny  - tameable, has Tamed/Owner, TypeInt for fur
  etfuturum.rabbit   - Et Futurum's backport of the 1.8 vanilla rabbit.
                       NOT tameable: it has no Tamed or Owner field at all.
                       It does support PersistenceRequired and CustomName.

Each is restored with its ORIGINAL NBT - same UUID, same variant, same
position - so it is the same entity rather than a fresh lookalike. Positions
are kept exactly as recorded and deliberately NOT snapped to the surface,
because these lived indoors and the HeightMap would put them on the roof.

Tameable species get tamed to OWNER. Untameable ones get PersistenceRequired
so at least they cannot quietly despawn again.

Server MUST be stopped.
"""
import math, os, shutil, subprocess, sys, time, zipfile

sys.path.insert(0, "/home/duduserver/mctools")
import nbtio

ROOT   = "/home/duduserver/minecraft/1.7.10"
BACKUP = f"{ROOT}/backups/2026-08-21-04-08-58/backup.zip"
OWNER  = "VerrassVerrass"
CENTRE = (4761.9, 9999.3)
SPAN   = 13                      # chunks either side
SPECIES = ("MoCreatures.Bunny", "etfuturum.rabbit")

BYTE, STRING, DOUBLE, FLOAT = 1, 8, 6, 5
APPLY = "--apply" in sys.argv


def uid(e):
    return (e.get("UUIDMost", (4, 0))[1], e.get("UUIDLeast", (4, 0))[1])


def chunks_span():
    cx0, cz0 = int(CENTRE[0]) >> 4, int(CENTRE[1]) >> 4
    for cx in range(cx0 - SPAN, cx0 + SPAN + 1):
        for cz in range(cz0 - SPAN, cz0 + SPAN + 1):
            yield cx, cz


class Live:
    def __init__(self): self.regions = {}

    def region(self, rx, rz):
        if (rx, rz) not in self.regions:
            p = f"{ROOT}/world/region/r.{rx}.{rz}.mca"
            self.regions[(rx, rz)] = nbtio.read_region(p) if os.path.exists(p) else {}
        return self.regions[(rx, rz)]

    def chunk(self, cx, cz):
        return self.region(cx >> 5, cz >> 5).get((cx & 31) + (cz & 31) * 32)

    def save(self):
        stamp = time.strftime("%Y%m%d-%H%M%S")
        for (rx, rz), chunks in self.regions.items():
            if not chunks:
                continue
            p = f"{ROOT}/world/region/r.{rx}.{rz}.mca"
            shutil.copy2(p, f"/home/duduserver/mctools/r.{rx}.{rz}.mca.PRE-RABBITS-{stamp}")
            nbtio.write_region(p, chunks)
            nbtio.read_region(p)
            print(f"   wrote r.{rx}.{rz}.mca ({len(chunks)} chunks, verified)")


def main():
    state = subprocess.run(["systemctl", "is-active", "minecraft"],
                           capture_output=True, text=True).stdout.strip()
    if state == "active" and APPLY:
        print("ABORT: stop the server first"); sys.exit(1)
    print(f"server: {state}\n")

    live = Live()

    present = set()
    for cx, cz in chunks_span():
        ch = live.chunk(cx, cz)
        if not ch:
            continue
        for e in (nbtio.entities(ch[2]) or []):
            if e.get("id", (0, ""))[1] in SPECIES:
                present.add(uid(e))
    print(f"alive now in the search area: {len(present)}")

    z = zipfile.ZipFile(BACKUP)
    members = {}
    for n in z.namelist():
        nn = n.replace("\\", "/")
        if nn.endswith(".mca") and "/DIM" not in nn and "world/region/" in nn:
            members[os.path.basename(nn)] = n

    cache, restored = {}, []
    for cx, cz in chunks_span():
        rx, rz = cx >> 5, cz >> 5
        if (rx, rz) not in cache:
            key = f"r.{rx}.{rz}.mca"
            if key not in members:
                cache[(rx, rz)] = {}
            else:
                open("/tmp/_rr.mca", "wb").write(z.read(members[key]))
                cache[(rx, rz)] = nbtio.read_region("/tmp/_rr.mca")
        bch = cache[(rx, rz)].get((cx & 31) + (cz & 31) * 32)
        if not bch:
            continue
        for e in (nbtio.entities(bch[2]) or []):
            sp = e.get("id", (0, ""))[1]
            if sp not in SPECIES or uid(e) in present:
                continue
            x, y, zz = e["Pos"][1][1]
            e["Motion"] = (9, (DOUBLE, [0.0, 0.0, 0.0]))
            e["FallDistance"] = (FLOAT, 0.0)
            e["PersistenceRequired"] = (BYTE, 1)
            tameable = "Tamed" in e or "Owner" in e
            if tameable:
                e["Tamed"] = (BYTE, 1)
                e["Owner"] = (STRING, OWNER)
            dch = live.chunk(int(math.floor(x)) >> 4, int(math.floor(zz)) >> 4)
            if not dch:
                print(f"   destination chunk missing for {sp} at {x:.0f},{zz:.0f}")
                continue
            nbtio.entities(dch[2]).append(e)
            present.add(uid(e))
            restored.append((sp, x, y, zz, tameable, uid(e)))

    print(f"\nrestoring {len(restored)} mob(s) missing from the live world:")
    for sp, x, y, zz, tam, u in restored:
        how = f"tamed to {OWNER}" if tam else "persistent (species cannot be tamed)"
        print(f"   {sp:20} {x:.2f},{y:.2f},{zz:.2f}  {how}")
        print(f"      uuid={u[0]}:{u[1]}")

    print()
    if not APPLY:
        print("DRY RUN - nothing written. Pass --apply.")
        return
    if restored:
        live.save()
    print("done")


if __name__ == "__main__":
    main()
