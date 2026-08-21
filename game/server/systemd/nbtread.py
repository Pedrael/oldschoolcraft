#!/usr/bin/env python3
"""Minimal NBT reader for 1.7.10 data.

Written for two jobs on this server:
  * dump the Forge item registry out of world/level.dat, so config entries use
    real registry names instead of guessed ones
  * read world/data/inventory-*.dat death snapshots for telemetry

1.7.10 NBT is big-endian and either gzip- or zlib-compressed, or raw.
"""
import gzip, struct, sys, zlib

TAG_END, TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG = 0, 1, 2, 3, 4
TAG_FLOAT, TAG_DOUBLE, TAG_BYTE_ARRAY, TAG_STRING = 5, 6, 7, 8
TAG_LIST, TAG_COMPOUND, TAG_INT_ARRAY = 9, 10, 11


class Reader:
    def __init__(self, data):
        self.d = data
        self.i = 0

    def raw(self, n):
        b = self.d[self.i:self.i + n]
        if len(b) != n:
            raise EOFError("truncated NBT")
        self.i += n
        return b

    def u1(self):  return self.raw(1)[0]
    def i1(self):  return struct.unpack(">b", self.raw(1))[0]
    def i2(self):  return struct.unpack(">h", self.raw(2))[0]
    def u2(self):  return struct.unpack(">H", self.raw(2))[0]
    def i4(self):  return struct.unpack(">i", self.raw(4))[0]
    def i8(self):  return struct.unpack(">q", self.raw(8))[0]
    def f4(self):  return struct.unpack(">f", self.raw(4))[0]
    def f8(self):  return struct.unpack(">d", self.raw(8))[0]

    def string(self):
        return self.raw(self.u2()).decode("utf-8", "replace")

    def payload(self, t):
        if t == TAG_BYTE:   return self.i1()
        if t == TAG_SHORT:  return self.i2()
        if t == TAG_INT:    return self.i4()
        if t == TAG_LONG:   return self.i8()
        if t == TAG_FLOAT:  return self.f4()
        if t == TAG_DOUBLE: return self.f8()
        if t == TAG_BYTE_ARRAY: return self.raw(self.i4())
        if t == TAG_STRING: return self.string()
        if t == TAG_END:
            return None            # some writers emit TAG_End payloads; tolerate them
        if t == TAG_LIST:
            it, n = self.u1(), self.i4()
            if it == TAG_END:
                return []          # empty list, element type unset - skip the count
            return [self.payload(it) for _ in range(max(0, n))]
        if t == TAG_COMPOUND:
            out = {}
            while True:
                tt = self.u1()
                if tt == TAG_END:
                    return out
                # Read the NAME first. `out[self.string()] = self.payload(tt)`
                # looks equivalent but Python evaluates the right-hand side
                # before the subscript, so it read the payload before the name
                # and desynced every nested compound.
                key = self.string()
                out[key] = self.payload(tt)
        if t == TAG_INT_ARRAY:
            n = self.i4()
            return [self.i4() for _ in range(n)]
        raise ValueError(f"unknown tag {t} at byte {self.i}")


def decompress(raw):
    if raw[:2] == b"\x1f\x8b":
        return gzip.decompress(raw)
    try:
        return zlib.decompress(raw)
    except zlib.error:
        return raw


def load(path):
    r = Reader(decompress(open(path, "rb").read()))
    t = r.u1()
    if t != TAG_COMPOUND:
        raise ValueError("not an NBT compound")
    r.string()               # root name, conventionally empty
    return r.payload(TAG_COMPOUND)


def walk(node, path=""):
    """Yield (path, value) for every leaf, so unknown structures are explorable."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, f"{path}/{k}")
    elif isinstance(node, list):
        for n, v in enumerate(node):
            yield from walk(v, f"{path}[{n}]")
    else:
        yield path, node


if __name__ == "__main__":
    doc = load(sys.argv[1])
    grep = sys.argv[2].lower() if len(sys.argv) > 2 else None
    for p, v in walk(doc):
        line = f"{p} = {v!r}"
        if grep is None or grep in line.lower():
            print(line[:300])
