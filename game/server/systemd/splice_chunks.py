#!/usr/bin/env python3
"""Splice chunks from a backup region file into the live one.

Region format: 4096B of location entries (1024 x [3-byte sector offset,
1-byte sector count]), 4096B of timestamps, then chunk payloads on 4096-byte
boundaries as [4-byte length][1-byte compression][data].
Chunk (cx, cz) sits at header index (cx & 31) + (cz & 31) * 32.

Per CLAUDE.md this REBUILDS THE WHOLE REGION FILE rather than patching sectors
in place: no stale sectors, no fragmentation, header always consistent.

Run with the server STOPPED. Writes to a temp file and only swaps it in after
verifying every chunk reads back.
"""
import os, shutil, struct, sys, time

SECTOR = 4096


def read_region(path):
    """-> {index: (timestamp, payload_bytes)} where payload includes the
    compression byte but not the 4-byte length prefix."""
    out = {}
    with open(path, "rb") as f:
        loc = f.read(SECTOR)
        ts = f.read(SECTOR)
        for i in range(1024):
            off = struct.unpack(">I", b"\x00" + loc[i * 4:i * 4 + 3])[0]
            cnt = loc[i * 4 + 3]
            if off == 0 or cnt == 0:
                continue
            f.seek(off * SECTOR)
            ln = struct.unpack(">I", f.read(4))[0]
            if ln <= 0:
                continue
            payload = f.read(ln)
            if len(payload) != ln:
                raise IOError(f"chunk {i}: short read ({len(payload)}/{ln})")
            stamp = struct.unpack(">I", ts[i * 4:i * 4 + 4])[0]
            out[i] = (stamp, payload)
    return out


def write_region(path, chunks):
    loc = bytearray(SECTOR)
    ts = bytearray(SECTOR)
    body = bytearray()
    sector = 2                                     # first two sectors are header
    for i in sorted(chunks):
        stamp, payload = chunks[i]
        blob = struct.pack(">I", len(payload)) + payload
        pad = (-len(blob)) % SECTOR
        blob += b"\x00" * pad
        n = len(blob) // SECTOR
        if n > 255:
            raise ValueError(f"chunk {i} needs {n} sectors (max 255)")
        loc[i * 4:i * 4 + 3] = struct.pack(">I", sector)[1:]
        loc[i * 4 + 3] = n
        ts[i * 4:i * 4 + 4] = struct.pack(">I", stamp)
        body += blob
        sector += n
    with open(path, "wb") as f:
        f.write(loc); f.write(ts); f.write(body)


def main():
    live, bak = sys.argv[1], sys.argv[2]
    coords = [tuple(int(v) for v in a.split(",")) for a in sys.argv[3:] if "," in a]
    apply = "--apply" in sys.argv
    if not coords:
        print("usage: splice_chunks.py LIVE BACKUP cx,cz [cx,cz ...] [--apply]")
        return

    L = read_region(live)
    B = read_region(bak)
    print(f"live   : {len(L)} chunks present")
    print(f"backup : {len(B)} chunks present\n")

    swapped, skipped = [], []
    for cx, cz in coords:
        i = (cx & 31) + (cz & 31) * 32
        if i not in B:
            skipped.append((cx, cz, "absent from backup")); continue
        if i not in L:
            skipped.append((cx, cz, "absent from live")); continue
        if L[i][1] == B[i][1]:
            skipped.append((cx, cz, "identical - nothing to do")); continue
        print(f"  restore chunk ({cx},{cz}) idx {i}: "
              f"{len(L[i][1])}B live -> {len(B[i][1])}B from backup")
        L[i] = B[i]
        swapped.append((cx, cz))

    for cx, cz, why in skipped:
        print(f"  skip    chunk ({cx},{cz}): {why}")

    print(f"\n{len(swapped)} chunk(s) to restore, {len(skipped)} skipped")
    if not apply:
        print("\nDRY RUN - nothing written. Pass --apply to write.")
        return
    if not swapped:
        print("nothing to do")
        return

    stamp = time.strftime("%Y%m%d-%H%M%S")
    backup_copy = f"{live}.before-splice-{stamp}"
    shutil.copy2(live, backup_copy)
    tmp = live + ".tmp"
    write_region(tmp, L)

    # verify the rebuilt file reads back cleanly before swapping it in
    V = read_region(tmp)
    if len(V) != len(L):
        os.remove(tmp)
        print(f"ABORT: verify failed ({len(V)} chunks read vs {len(L)} written)")
        return
    for cx, cz in swapped:
        i = (cx & 31) + (cz & 31) * 32
        if V[i][1] != B[i][1]:
            os.remove(tmp)
            print(f"ABORT: chunk ({cx},{cz}) did not verify")
            return

    os.replace(tmp, live)
    print(f"\nwritten. previous region saved as:\n  {backup_copy}")
    print(f"verified {len(V)} chunks readable, {len(swapped)} restored")


if __name__ == "__main__":
    main()
