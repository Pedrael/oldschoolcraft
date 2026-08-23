#!/usr/bin/env python3
"""NBT -> SNBT, so a grave can be built with setblock's dataTag.

The penalty path has to hand a player's real inventory to a grave block, and
setblock only takes text. Tinkers' tools, enchanted gear and Thaumcraft items
all carry deep nested NBT, so a naive str() of the tree loses them silently -
which would mean quietly deleting somebody's hammer.

Types must be suffixed exactly or Minecraft reads them back as the wrong thing:
    byte 1b   short 1s   int 1   long 1L   float 1.0f   double 1.0d
Byte arrays have no 1.7.10 SNBT form at all, so anything containing one is
REFUSED rather than mangled - the caller falls back to leaving the player
their items.
"""
BYTE, SHORT, INT, LONG, FLOAT, DOUBLE, BYTE_ARRAY, STRING, LIST, COMPOUND, INT_ARRAY = range(1, 12)


class Unserialisable(Exception):
    """This value has no faithful SNBT form. Refuse rather than corrupt."""


def esc(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def snbt(t, v):
    if t == BYTE:   return f"{v}b"
    if t == SHORT:  return f"{v}s"
    if t == INT:    return f"{v}"
    if t == LONG:   return f"{v}L"
    if t == FLOAT:  return f"{v}f"
    if t == DOUBLE: return f"{v}d"
    if t == STRING: return esc(v)
    if t == INT_ARRAY:
        return "[" + ",".join(str(x) for x in v) + "]"
    if t == BYTE_ARRAY:
        # 1.7.10 has no byte-array literal. Refusing keeps the item intact
        # somewhere else rather than writing a grave that silently drops it.
        raise Unserialisable("byte array")
    if t == LIST:
        et, items = v
        return "[" + ",".join(snbt(et, i) for i in items) + "]"
    if t == COMPOUND:
        return "{" + ",".join(f"{k}:{snbt(tt, vv)}" for k, (tt, vv) in v.items()) + "}"
    raise Unserialisable(f"tag {t}")


def items_to_snbt(stacks, size=None):
    """The Items list plus a matching size, which caps what a grave will hold."""
    parts = []
    for i, s in enumerate(stacks):
        if not isinstance(s, dict):
            continue
        s = dict(s)
        s["Slot"] = (BYTE, i)          # renumber: gaps make graves drop stacks
        parts.append(snbt(COMPOUND, s))
    n = len(parts) if size is None else size
    return "{size:%d,Items:[%s]}" % (n, ",".join(parts))
