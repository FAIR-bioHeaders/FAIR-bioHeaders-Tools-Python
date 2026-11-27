"""Check python-paths.txt against a Tools repository at a cut SHA.

usage: python3 -I check_paths.py <tools-git-dir> <cut-sha> <python-paths.txt>
Exits non-zero on any problem. Reports: entries missing at cut (must be historical),
entries never present in history, history paths neither kept nor explicitly excluded.
"""

import subprocess
import sys

EXCLUDED = [
    "galaxy/",
    ".github/workflows/galaxy-tools.yml",
    "tests/galaxy_metadata_tool_test.py",
]


def git(*a):
    return subprocess.run(
        ["git", "-C", sys.argv[1], "-c", "core.quotepath=off", *a],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def matches(path, entry):
    return path == entry.rstrip("/") or path.startswith(entry.rstrip("/") + "/")


gitdir, cut, listfile = sys.argv[1:4]
entries = [ln.strip() for ln in open(listfile) if ln.strip() and not ln.startswith("#")]
cut_paths = set(git("ls-tree", "-r", "--name-only", cut).splitlines())
hist = set(
    p
    for p in git("log", cut, "--format=", "--name-only", "--no-renames").splitlines()
    if p
)
bad = 0
historical_section = False
for line in open(listfile):
    if line.startswith("## 8."):
        historical_section = True
    e = line.strip()
    if not e or e.startswith("#"):
        continue
    at_cut = any(matches(p, e) for p in cut_paths)
    in_hist = any(matches(p, e) for p in hist)
    if historical_section and at_cut:
        print(f"HISTORICAL ENTRY PRESENT AT CUT: {e}")
        bad += 1
    if not historical_section and not at_cut:
        print(f"MISSING AT CUT: {e}")
        bad += 1
    if not in_hist:
        print(f"NEVER IN HISTORY: {e}")
        bad += 1
for p in sorted(hist | cut_paths):
    kept = any(matches(p, e) for e in entries)
    excl = any(matches(p, x) for x in EXCLUDED)
    if kept and excl:
        print(f"KEPT BUT EXCLUDED: {p}")
        bad += 1
    elif not kept and not excl:
        print(f"UNACCOUNTED: {p}")
        bad += 1
kept_cut = sorted(p for p in cut_paths if any(matches(p, e) for e in entries))
excl_cut = sorted(p for p in cut_paths if any(matches(p, x) for x in EXCLUDED))
print(
    f"entries={len(entries)} cut_files={len(cut_paths)} kept_at_cut={len(kept_cut)} "
    f"excluded_at_cut={len(excl_cut)} history_paths={len(hist)} problems={bad}"
)
sys.exit(1 if bad else 0)
