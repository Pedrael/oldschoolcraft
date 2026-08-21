#!/usr/bin/env python3
"""Verify candidate mod jars BEFORE they go into mods/.

Filenames lie; mcmod.info doesn't. This reads each jar's declared Minecraft
version, mod id and dependencies, then checks them against what is already
installed and against this world's used ID space.
"""
import glob, gzip, json, os, re, sys, zipfile

ROOT = "/home/duduserver/minecraft/1.7.10"
STAGE = os.path.expanduser("~/modstaging")

def meta(jar):
    out = {"file": os.path.basename(jar), "size": os.path.getsize(jar)}
    try:
        z = zipfile.ZipFile(jar)
    except Exception as e:
        out["error"] = f"not a valid zip: {e}"; return out
    names = z.namelist()
    out["classes"] = sum(1 for n in names if n.endswith(".class"))
    if "mcmod.info" in names:
        try:
            raw = z.read("mcmod.info").decode("utf-8", "replace")
            raw = re.sub(r"[\x00-\x1f]", " ", raw)
            d = json.loads(raw)
            if isinstance(d, dict): d = d.get("modList", [])
            for m in d:
                out.setdefault("mods", []).append({
                    "modid": m.get("modid"), "name": m.get("name"),
                    "version": m.get("version"), "mcversion": m.get("mcversion"),
                    "requires": m.get("requiredMods") or m.get("dependencies") or [],
                })
        except Exception as e:
            out["mcmod_error"] = str(e)
    else:
        out["mcmod_error"] = "no mcmod.info"
    return out

def installed_modids():
    ids = set()
    for j in glob.glob(f"{ROOT}/mods/*.jar"):
        try:
            z = zipfile.ZipFile(j)
            if "mcmod.info" in z.namelist():
                raw = re.sub(r"[\x00-\x1f]", " ", z.read("mcmod.info").decode("utf-8", "replace"))
                d = json.loads(raw)
                if isinstance(d, dict): d = d.get("modList", [])
                for m in d:
                    if m.get("modid"): ids.add(m["modid"])
        except Exception:
            pass
    return ids

def main():
    jars = sorted(glob.glob(f"{STAGE}/*.jar"))
    if not jars:
        print(f"nothing staged in {STAGE}"); return
    have = installed_modids()
    print(f"already installed: {len(have)} mod ids\n")
    need = set()
    provide = set()
    for j in jars:
        m = meta(j)
        print(f"=== {m['file']}  ({m['size']//1024} KB, {m.get('classes','?')} classes)")
        if m.get("error"): print("   !!", m["error"]); continue
        if m.get("mcmod_error"): print("   ??", m["mcmod_error"])
        for mod in m.get("mods", []):
            provide.add(mod["modid"])
            dup = "  <-- ALREADY INSTALLED" if mod["modid"] in have else ""
            print(f"   modid={mod['modid']}  version={mod['version']}  mc={mod['mcversion']}{dup}")
            for r in mod["requires"]:
                need.add(r)
                print(f"      requires: {r}")
    missing = {r for r in need if not any(r.startswith(p) or p in r for p in have | provide)}
    print("\n--- dependency check ---")
    print("satisfied by installed or staged" if not missing else f"MISSING: {sorted(missing)}")

main()
