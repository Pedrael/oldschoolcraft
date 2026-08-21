#!/usr/bin/env python3
"""Move Dudu's cats off Vera's base, and give her back her bunny, tamed.

Three edits, all offline on the region files (server MUST be stopped):

  1. RELOCATE  every tamed Kitty owned by DuduPhudu within RADIUS of Vera's
     base to Dudu's own base, landing on the surface height read out of the
     destination chunk's HeightMap rather than a guessed Y.

  2. RESTORE   the bunny that was alive in the 04:09 backup and is gone now,
     re-inserted with its ORIGINAL NBT - same UUID, same TypeInt, same age.
     It is the same entity, not a lookalike.

  3. TAME      that bunny and any other bunny near her base to Vera, with
     PersistenceRequired so they cannot despawn, and Sitting=0 so they behave
     normally.

Entities are moved between chunks properly - removed from the source chunk's
Entities list and appended to the destination's - so Minecraft never has to
emit "Wrong location!" and shuffle them itself.
"""
import math, os, shutil, subprocess, sys, time, zipfile

sys.path.insert(0, "/home/duduserver/mctools")
import nbtio

ROOT   = "/home/duduserver/minecraft/1.7.10"
BACKUP = f"{ROOT}/backups/2026-08-21-04-08-58/backup.zip"

VERA_NAME = "VerrassVerrass"
VERA   = (4761.9, 9999.3)      # her base
DUDU   = (4985.0, 10288.0)     # where the cats are going
RADIUS = 120

BYTE, SHORT, INT, LONG, FLOAT, DOUBLE, STRING = 1, 2, 3, 4, 5, 6, 8
APPLY = "--apply" in sys.argv


def region_of(cx, cz): return cx >> 5, cz >> 5
def index_of(cx, cz):  return (cx & 31) + (cz & 31) * 32


class World:
    """Lazily-loaded region files, written back together at the end."""
    def __init__(self, root): self.root, self.regions = root, {}

    def region(self, rx, rz):
        if (rx, rz) not in self.regions:
            p = f"{self.root}/world/region/r.{rx}.{rz}.mca"
            self.regions[(rx, rz)] = nbtio.read_region(p) if os.path.exists(p) else {}
        return self.regions[(rx, rz)]

    def chunk(self, cx, cz):
        return self.region(*region_of(cx, cz)).get(index_of(cx, cz))

    def save(self, apply):
        stamp = time.strftime("%Y%m%d-%H%M%S")
        for (rx, rz), chunks in self.regions.items():
            if not chunks:
                continue
            p = f"{self.root}/world/region/r.{rx}.{rz}.mca"
            if not apply:
                continue
            shutil.copy2(p, f"/home/duduserver/mctools/r.{rx}.{rz}.mca.PRE-MOBS-{stamp}")
            nbtio.write_region(p, chunks)
            nbtio.read_region(p)          # prove it reads back
            print(f"   wrote {os.path.basename(p)} ({len(chunks)} chunks, verified)")


def surface_y(world, x, z):
    """Ground level from the chunk's own HeightMap, so nothing lands in rock."""
    cx, cz = int(math.floor(x)) >> 4, int(math.floor(z)) >> 4
    ch = world.chunk(cx, cz)
    if not ch:
        return None
    hm = ch[2].get("Level", (0, {}))[1].get("HeightMap")
    if not hm:
        return None
    lx, lz = int(math.floor(x)) & 15, int(math.floor(z)) & 15
    return float(hm[1][lz * 16 + lx])


def pos_of(e):
    return [v for v in e["Pos"][1][1]]


def set_pos(e, x, y, z):
    e["Pos"] = (9, (DOUBLE, [float(x), float(y), float(z)]))
    e["Motion"] = (9, (DOUBLE, [0.0, 0.0, 0.0]))
    e["FallDistance"] = (FLOAT, 0.0)
    e["OnGround"] = (BYTE, 1)


def tame_to(e, who):
    e["Tamed"] = (BYTE, 1)
    e["Owner"] = (STRING, who)
    e["PersistenceRequired"] = (BYTE, 1)
    if "Sitting" in e:
        e["Sitting"] = (BYTE, 0)


def main():
    state = subprocess.run(["systemctl", "is-active", "minecraft"],
                           capture_output=True, text=True).stdout.strip()
    if state == "active" and APPLY:
        print("ABORT: stop the server first - it would overwrite these edits")
        sys.exit(1)
    print(f"server: {state}\n")

    w = World(ROOT)

    # ---- 1. cats off her base -------------------------------------------
    print("1. RELOCATING CATS")
    moved, dest_slots = [], []
    ring = [(dx, dz) for dx in range(-6, 7, 3) for dz in range(-6, 7, 3)]
    for cx in range(-9, 10):
        for cz in range(-9, 10):
            pass
    for rx in range(int(VERA[0]) // 512 - 1, int(VERA[0]) // 512 + 2):
        pass

    # sweep the chunks around Vera for cats
    vcx, vcz = int(VERA[0]) >> 4, int(VERA[1]) >> 4
    span = RADIUS // 16 + 1
    for cx in range(vcx - span, vcx + span + 1):
        for cz in range(vcz - span, vcz + span + 1):
            ch = w.chunk(cx, cz)
            if not ch:
                continue
            ents = nbtio.entities(ch[2])
            if ents is None:
                continue
            for e in list(ents):
                if e.get("id", (0, ""))[1] != "MoCreatures.Kitty":
                    continue
                if e.get("Tamed", (BYTE, 0))[1] != 1:
                    continue
                if e.get("Owner", (STRING, ""))[1] != "DuduPhudu":
                    continue
                x, y, z = pos_of(e)
                if math.hypot(x - VERA[0], z - VERA[1]) > RADIUS:
                    continue
                ents.remove(e)
                moved.append((e, (cx, cz), (round(x), round(y), round(z))))

    print(f"   cats to move: {len(moved)}")
    if moved:
        # Build candidate columns first and keep only the flat ones. HeightMap
        # returns the top of a TREE for a wooded column, and dropping a cat
        # twenty blocks onto stone hurts it.
        cand = []
        for i in range(-8, 9):
            for j in range(-8, 9):
                nx, nz = DUDU[0] + i * 2, DUDU[1] + j * 2
                sy = surface_y(w, nx, nz)
                if sy is not None:
                    cand.append((nx, sy, nz))
        if cand:
            med = sorted(c[1] for c in cand)[len(cand) // 2]
            flat = [c for c in cand if abs(c[1] - med) <= 2]
            print(f"   destination ground level ~y={med:.0f}, "
                  f"{len(flat)} flat columns of {len(cand)} candidates")
        else:
            flat, med = [], 64
        placed = 0
        for e, src, oldpos in moved:
            if not flat:
                print("   WARNING: no flat ground found at the destination")
                break
            nx, ny, nz = flat[placed % len(flat)]
            set_pos(e, nx, ny, nz)
            dch = w.chunk(int(nx) >> 4, int(nz) >> 4)
            if not dch:
                print(f"   WARNING: destination chunk missing at {nx:.0f},{nz:.0f}")
                continue
            nbtio.entities(dch[2]).append(e)
            dest_slots.append((oldpos, (round(nx), round(ny), round(nz))))
            placed += 1
        print(f"   placed at Dudu's base: {placed}")
        for o, d in dest_slots[:4]:
            print(f"      {o} -> {d}")
        if len(dest_slots) > 4:
            print(f"      ... and {len(dest_slots)-4} more")

    # ---- 2. the bunny from the backup ------------------------------------
    print("\n2. RESTORING THE BUNNY FROM THE 04:09 BACKUP")
    live_uuids = set()
    bunnies_live = []
    for cx in range(vcx - span, vcx + span + 1):
        for cz in range(vcz - span, vcz + span + 1):
            ch = w.chunk(cx, cz)
            if not ch:
                continue
            for e in (nbtio.entities(ch[2]) or []):
                if e.get("id", (0, ""))[1] == "MoCreatures.Bunny":
                    live_uuids.add((e["UUIDMost"][1], e["UUIDLeast"][1]))
                    bunnies_live.append(e)

    restored = 0
    with zipfile.ZipFile(BACKUP) as z:
        names = {}
        for n in z.namelist():
            if not n.endswith(".mca"):
                continue
            # must be the OVERWORLD: DIM-1/DIM1 carry identical basenames and
            # would otherwise silently win this lookup
            norm = n.replace("\\", "/")
            if "/DIM" in norm or norm.startswith("DIM"):
                continue
            if "world/region/" not in norm and not norm.startswith("region/"):
                continue
            names[os.path.basename(norm)] = n
        for cx in range(vcx - span, vcx + span + 1):
            for cz in range(vcz - span, vcz + span + 1):
                rx, rz = region_of(cx, cz)
                fn = names.get(f"r.{rx}.{rz}.mca")
                if not fn:
                    continue
                tmp = "/tmp/_bk.mca"
                open(tmp, "wb").write(z.read(fn))
                try:
                    br = nbtio.read_region(tmp)
                except Exception:
                    continue
                bch = br.get(index_of(cx, cz))
                if not bch:
                    continue
                for e in (nbtio.entities(bch[2]) or []):
                    if e.get("id", (0, ""))[1] != "MoCreatures.Bunny":
                        continue
                    uid = (e["UUIDMost"][1], e["UUIDLeast"][1])
                    if uid in live_uuids:
                        continue
                    x, y, z_ = pos_of(e)
                    tame_to(e, VERA_NAME)
                    # Keep its ORIGINAL position. It was indoors; the HeightMap
                    # would put it on the roof of her house instead.
                    set_pos(e, x, y, z_)
                    dch = w.chunk(int(x) >> 4, int(z_) >> 4)
                    if not dch:
                        continue
                    nbtio.entities(dch[2]).append(e)
                    restored += 1
                    print(f"   restored bunny uuid={uid[0]}:{uid[1]} "
                          f"type={e['TypeInt'][1]} at {x:.2f},{y:.2f},{z_:.2f} "
                          f"-> tamed to {VERA_NAME}")
    if not restored:
        print("   (none found in the backup that is missing from the live world)")

    # ---- 3. tame the survivors ------------------------------------------
    print(f"\n3. TAMING THE {len(bunnies_live)} BUNNIES ALREADY THERE")
    for e in bunnies_live:
        tame_to(e, VERA_NAME)
        x, y, z_ = pos_of(e)
        print(f"   type={e['TypeInt'][1]} at {x:.0f},{y:.0f},{z_:.0f} -> {VERA_NAME}")

    print()
    if not APPLY:
        print("DRY RUN - nothing written. Pass --apply.")
        return
    w.save(True)
    print("\ndone")


if __name__ == "__main__":
    main()
