#!/usr/bin/env python3
"""Search mod jars for archive entries matching one or more terms.

Usage:
    search_mods.py MODS_DIR TERM [TERM ...]

Each mod jar in MODS_DIR is opened as a zip archive. By default every
entry path (class file, texture, lang file, etc.) containing one of the
given terms is reported. With --content, the raw bytes of each entry are
also searched — this finds terms embedded in compiled .class files (e.g.
a potion effect name referenced in bytecode) the same way `grep -a` would
on any binary, since Java's constant pool stores string literals as plain
UTF-8 text.
"""

import argparse
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

CONTEXT_BYTES = 24
MAX_SNIPPETS_PER_ENTRY = 3


@dataclass
class Match:
    entry: str
    kind: str  # "name" or "content"
    snippet: str | None = None


def find_jars(mods_dir: Path, recursive: bool) -> list[Path]:
    pattern = "**/*.jar" if recursive else "*.jar"
    return sorted(mods_dir.glob(pattern))


def make_snippet(data: bytes, pos: int, needle_len: int) -> str:
    start = max(0, pos - CONTEXT_BYTES)
    end = min(len(data), pos + needle_len + CONTEXT_BYTES)
    window = data[start:end].decode("latin-1")
    printable = "".join(c if c.isprintable() and c.encode("latin-1")[0] < 0x7F else "." for c in window)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(data) else ""
    return f"{prefix}{printable}{suffix}"


def search_entry_content(data: bytes, needle: str, case_sensitive: bool) -> list[str]:
    haystack = data if case_sensitive else data.lower()
    needle_bytes = needle.encode("utf-8") if case_sensitive else needle.lower().encode("utf-8")
    snippets = []
    pos = haystack.find(needle_bytes)
    while pos != -1 and len(snippets) < MAX_SNIPPETS_PER_ENTRY:
        snippets.append(make_snippet(data, pos, len(needle_bytes)))
        pos = haystack.find(needle_bytes, pos + 1)
    return snippets


def search_jar(
    jar_path: Path, terms: list[str], case_sensitive: bool, content: bool
) -> dict[str, list[Match]]:
    matches: dict[str, list[Match]] = {term: [] for term in terms}
    try:
        with zipfile.ZipFile(jar_path) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                name = info.filename
                name_haystack = name if case_sensitive else name.lower()
                data = None
                for term in terms:
                    needle = term if case_sensitive else term.lower()
                    if needle in name_haystack:
                        matches[term].append(Match(name, "name"))
                    if content:
                        if data is None:
                            try:
                                data = zf.read(info)
                            except (zipfile.BadZipFile, OSError):
                                data = b""
                        for snippet in search_entry_content(data, term, case_sensitive):
                            matches[term].append(Match(name, "content", snippet))
    except zipfile.BadZipFile:
        print(f"warning: {jar_path.name} is not a valid zip/jar, skipping", file=sys.stderr)
    return matches


def main() -> int:
    parser = argparse.ArgumentParser(description="Search mod jars for matching archive entries.")
    parser.add_argument("mods_dir", type=Path, help="Folder containing mod .jar files")
    parser.add_argument("terms", nargs="+", help="One or more terms to search for")
    parser.add_argument("-r", "--recursive", action="store_true", help="Also search jars in subfolders")
    parser.add_argument("-c", "--case-sensitive", action="store_true", help="Match case-sensitively")
    parser.add_argument(
        "-k",
        "--content",
        action="store_true",
        help="Also search inside entry contents (e.g. strings embedded in .class files), not just entry names",
    )
    args = parser.parse_args()

    if not args.mods_dir.is_dir():
        parser.error(f"{args.mods_dir} is not a directory")

    jars = find_jars(args.mods_dir, args.recursive)
    if not jars:
        print(f"No .jar files found in {args.mods_dir}", file=sys.stderr)
        return 1

    found_any = False
    for jar_path in jars:
        matches = search_jar(jar_path, args.terms, args.case_sensitive, args.content)
        jar_hits = {term: entries for term, entries in matches.items() if entries}
        if not jar_hits:
            continue
        found_any = True
        print(f"\n{jar_path.name}")
        for term, entries in jar_hits.items():
            print(f"  [{term}] ({len(entries)} match{'es' if len(entries) != 1 else ''})")
            for m in entries:
                if m.kind == "name":
                    print(f"    {m.entry}")
                else:
                    print(f"    {m.entry}  ->  {m.snippet}")

    if not found_any:
        print("No matches found.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
