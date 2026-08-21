#!/usr/bin/env python3
"""Make every quest-line generator lint its own output.

A checkbox quest used as a prerequisite locks an entire chapter while still
showing its tasks ticked green. That cannot be caught by eye, so it should not
depend on remembering to check: each generator now runs bq_lint over the
database it just wrote and repairs the graph before it exits.
"""
import re, shutil, sys, time

TOOLS = "/home/duduserver/mctools"
GENERATORS = ["add_questline.py", "add_teaching_lines.py", "add_twilight_line.py",
              "add_powersuit_line.py", "add_cartographer_line.py", "add_shard_daily.py"]

OLD = '''if __name__ == "__main__":
    main()'''

NEW = '''def _lint_after_write():
    """A checkbox quest used as a prerequisite locks a whole chapter while
    still showing its tasks ticked - indistinguishable from broken data in
    game. Never leave the database in that state; see bq_lint.py."""
    import os as _os, sys as _sys
    if "--apply" not in _sys.argv:
        return
    _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
    try:
        import bq_lint as _lint
    except ImportError:
        print("WARNING: bq_lint.py not found - quest graph NOT verified")
        return
    rc, problems = _lint.check(DB, fix=True, quiet=True)
    if problems:
        print("\\nbq_lint repaired: " + "; ".join(problems))
    else:
        print("\\nbq_lint: quest graph clean")


if __name__ == "__main__":
    main()
    _lint_after_write()'''

changed = 0
for g in GENERATORS:
    path = f"{TOOLS}/{g}"
    s = open(path, encoding="utf-8").read()
    if "_lint_after_write" in s:
        print(f"  {g}: already wired"); continue
    if s.count(OLD) != 1:
        print(f"  {g}: ABORT - tail matched {s.count(OLD)}x"); sys.exit(1)
    # DB must be a module-level constant for the lint call to see it
    if not re.search(r"^DB\s*=", s, re.M):
        print(f"  {g}: ABORT - no module-level DB constant"); sys.exit(1)
    shutil.copy2(path, path + ".bak-" + time.strftime("%Y%m%d-%H%M%S"))
    open(path, "w", encoding="utf-8").write(s.replace(OLD, NEW))
    print(f"  {g}: wired")
    changed += 1

print(f"\n{changed} generator(s) now lint their own output")
