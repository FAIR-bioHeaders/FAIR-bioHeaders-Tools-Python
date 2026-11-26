"""Compare two wheel/sdist archives member by member (names + sha256 of bytes).

usage: python3 -I compare_dists.py <reference> <candidate>
Prints members only in one side and members whose bytes differ (with a unified diff
for small text members). Exit 0 when the member sets and bytes are identical.
"""

import difflib
import hashlib
import sys
import tarfile
import zipfile


def members(path):
    out = {}
    if path.endswith(".whl"):
        with zipfile.ZipFile(path) as z:
            for n in z.namelist():
                out[n] = z.read(n)
    else:
        with tarfile.open(path) as t:
            for m in t.getmembers():
                if m.isfile():
                    name = m.name.split("/", 1)[1] if "/" in m.name else m.name
                    out[name] = t.extractfile(m).read()
    return out


ref, cand = members(sys.argv[1]), members(sys.argv[2])
only_ref = sorted(set(ref) - set(cand))
only_cand = sorted(set(cand) - set(ref))
diff = sorted(n for n in set(ref) & set(cand) if ref[n] != cand[n])
print(
    f"{sys.argv[1]} vs {sys.argv[2]}: members ref={len(ref)} cand={len(cand)} "
    f"only_ref={len(only_ref)} only_cand={len(only_cand)} differing={len(diff)}"
)
for n in only_ref:
    print("  ONLY IN REFERENCE:", n)
for n in only_cand:
    print("  ONLY IN CANDIDATE:", n)
for n in diff:
    print(
        "  DIFFERS:",
        n,
        hashlib.sha256(ref[n]).hexdigest()[:12],
        hashlib.sha256(cand[n]).hexdigest()[:12],
    )
    if len(ref[n]) < 200000 and len(cand[n]) < 200000:
        try:
            a = ref[n].decode().splitlines()
            b = cand[n].decode().splitlines()
            for ln in list(difflib.unified_diff(a, b, "ref", "cand", n=0, lineterm=""))[
                2:40
            ]:
                print("    " + ln)
        except UnicodeDecodeError:
            pass
sys.exit(1 if (only_ref or only_cand or diff) else 0)
