#!/usr/bin/env python3
"""Typed NBT read/write for 1.7.10, so edited chunks survive a round trip.

nbtread.py returns plain Python values, which is fine for inspection but loses
the tag type: an int could be a byte, short, int or long, and guessing wrong on
write corrupts the chunk. Everything here carries its type.

    Tag        = (type_id, value)
    compound   value = dict{name: Tag}   preserving insertion order
    list       value = (elem_type, [raw values])

read_region / write_region handle the .mca container, rebuilding the whole file
rather than patching sectors, as CLAUDE.md requires.
"""
import gzip, struct, zlib

END, BYTE, SHORT, INT, LONG, FLOAT, DOUBLE, BYTE_ARRAY, STRING, LIST, COMPOUND, INT_ARRAY = range(12)
SECTOR = 4096


# ------------------------------------------------------------------ read --
class R:
    def __init__(self, d):
        self.d, self.i = d, 0

    def raw(self, n):
        b = self.d[self.i:self.i + n]
        if len(b) != n:
            raise EOFError("truncated NBT")
        self.i += n
        return b

    def u1(self): return self.raw(1)[0]
    def i1(self): return struct.unpack(">b", self.raw(1))[0]
    def i2(self): return struct.unpack(">h", self.raw(2))[0]
    def u2(self): return struct.unpack(">H", self.raw(2))[0]
    def i4(self): return struct.unpack(">i", self.raw(4))[0]
    def i8(self): return struct.unpack(">q", self.raw(8))[0]
    def f4(self): return struct.unpack(">f", self.raw(4))[0]
    def f8(self): return struct.unpack(">d", self.raw(8))[0]
    def s(self): return self.raw(self.u2()).decode("utf-8", "replace")

    def val(self, t):
        if t == BYTE:   return self.i1()
        if t == SHORT:  return self.i2()
        if t == INT:    return self.i4()
        if t == LONG:   return self.i8()
        if t == FLOAT:  return self.f4()
        if t == DOUBLE: return self.f8()
        if t == BYTE_ARRAY: return self.raw(self.i4())
        if t == STRING: return self.s()
        if t == END:    return None
        if t == LIST:
            et, n = self.u1(), self.i4()
            return (et, [self.val(et) for _ in range(max(0, n))])
        if t == COMPOUND:
            out = {}
            while True:
                tt = self.u1()
                if tt == END:
                    return out
                nm = self.s()                  # name BEFORE payload
                out[nm] = (tt, self.val(tt))
            return out
        if t == INT_ARRAY:
            n = self.i4()
            return [self.i4() for _ in range(n)]
        raise ValueError(f"unknown tag {t} at {self.i}")


# ----------------------------------------------------------------- write --
class W:
    def __init__(self): self.b = bytearray()
    def u1(self, v): self.b.append(v & 0xFF)
    def i1(self, v): self.b += struct.pack(">b", v)
    def i2(self, v): self.b += struct.pack(">h", v)
    def u2(self, v): self.b += struct.pack(">H", v)
    def i4(self, v): self.b += struct.pack(">i", v)
    def i8(self, v): self.b += struct.pack(">q", v)
    def f4(self, v): self.b += struct.pack(">f", v)
    def f8(self, v): self.b += struct.pack(">d", v)

    def s(self, v):
        e = v.encode("utf-8")
        self.u2(len(e)); self.b += e

    def val(self, t, v):
        if t == BYTE:   return self.i1(v)
        if t == SHORT:  return self.i2(v)
        if t == INT:    return self.i4(v)
        if t == LONG:   return self.i8(v)
        if t == FLOAT:  return self.f4(v)
        if t == DOUBLE: return self.f8(v)
        if t == BYTE_ARRAY:
            self.i4(len(v)); self.b += v; return
        if t == STRING: return self.s(v)
        if t == END:    return
        if t == LIST:
            et, items = v
            self.u1(et); self.i4(len(items))
            for it in items: self.val(et, it)
            return
        if t == COMPOUND:
            for nm, (tt, vv) in v.items():
                self.u1(tt); self.s(nm); self.val(tt, vv)
            self.u1(END); return
        if t == INT_ARRAY:
            self.i4(len(v))
            for x in v: self.i4(x)
            return
        raise ValueError(f"cannot write tag {t}")


def parse(raw):
    r = R(raw)
    t = r.u1()
    if t != COMPOUND:
        raise ValueError("root is not a compound")
    name = r.s()
    return name, r.val(COMPOUND)


def serialise(name, comp):
    w = W()
    w.u1(COMPOUND); w.s(name); w.val(COMPOUND, comp)
    return bytes(w.b)


# ---------------------------------------------------------------- region --
def read_region(path):
    """{index: (timestamp, root_name, compound)}"""
    out = {}
    blob = open(path, "rb").read()
    loc, ts = blob[:SECTOR], blob[SECTOR:SECTOR * 2]
    for i in range(1024):
        off = struct.unpack(">I", b"\x00" + loc[i * 4:i * 4 + 3])[0]
        cnt = loc[i * 4 + 3]
        if not off or not cnt:
            continue
        base = off * SECTOR
        ln = struct.unpack(">I", blob[base:base + 4])[0]
        if ln <= 0:
            continue
        comp = blob[base + 4]
        data = blob[base + 5: base + 4 + ln]
        raw = zlib.decompress(data) if comp == 2 else gzip.decompress(data)
        nm, c = parse(raw)
        out[i] = (struct.unpack(">I", ts[i * 4:i * 4 + 4])[0], nm, c)
    return out


def write_region(path, chunks):
    loc, tsb, body = bytearray(SECTOR), bytearray(SECTOR), bytearray()
    sector = 2
    for i in sorted(chunks):
        stamp, nm, c = chunks[i]
        payload = b"\x02" + zlib.compress(serialise(nm, c), 6)
        blob = struct.pack(">I", len(payload)) + payload
        blob += b"\x00" * ((-len(blob)) % SECTOR)
        n = len(blob) // SECTOR
        if n > 255:
            raise ValueError(f"chunk {i} needs {n} sectors")
        loc[i * 4:i * 4 + 3] = struct.pack(">I", sector)[1:]
        loc[i * 4 + 3] = n
        tsb[i * 4:i * 4 + 4] = struct.pack(">I", stamp)
        body += blob
        sector += n
    with open(path, "wb") as f:
        f.write(loc); f.write(tsb); f.write(body)


def entities(chunk):
    """The Entities list value, as (elem_type, [compound, ...])."""
    lvl = chunk.get("Level")
    if not lvl:
        return None
    ent = lvl[1].get("Entities")
    if not ent:
        return None
    # ent is (LIST, (elem_type, [items])) - callers want the items themselves,
    # and want the SAME list object so appends/removals stick.
    return ent[1][1]
