#!/usr/bin/env bash
# usage: smoke_installed.sh <venv-dir> <examples-dir> <reference-entry_points.txt> <dist files...>
# Installs the given wheels/sdists into a fresh venv, then from /tmp (outside any
# checkout) checks the 13 console scripts against the reference entry_points.txt,
# runs each command's --help, the release.yml smoke commands, the import policy
# (bioheaders under -W error; fhr warns exactly once) and fhr-distribution scripts.
set -euo pipefail
VENV=$1 EX=$2 REF=$3; shift 3
rm -rf "$VENV"; uv venv -q --seed -p python3.13 "$VENV"
"$VENV/bin/python" -m pip -q install "$@"
cd /tmp
"$VENV/bin/python" -I - "$REF" <<'PY'
import configparser, sys
from importlib.metadata import distribution
ref = configparser.ConfigParser(); ref.read(sys.argv[1])
want = dict(ref["console_scripts"])
got = {e.name: e.value for e in distribution("fair-bioheaders").entry_points if e.group == "console_scripts"}
assert got == want, (sorted(set(got) ^ set(want)), {k: (got.get(k), want.get(k)) for k in want if got.get(k) != want.get(k)})
print(f"PASS entry points: {len(got)} console scripts identical to 0.13.1 (names and targets)")
fhr = distribution("fhr")
print("fhr dist", fhr.version, "requires", fhr.requires)
fhr_eps = {e.name: e.value for e in fhr.entry_points if e.group == "console_scripts"}
assert fhr_eps == {k: v for k, v in want.items() if k.startswith("fhr-")}, fhr_eps
print(f"PASS fhr distribution declares the same {len(fhr_eps)} fhr-* scripts")
PY
for c in $(sed -n '/console_scripts/,/^\[/p' "$REF" | grep '=' | cut -d= -f1 | tr -d ' '); do
  test -x "$VENV/bin/$c" || { echo "FAIL missing $c"; exit 1; }
  "$VENV/bin/$c" --help >/dev/null || { echo "FAIL $c --help"; exit 1; }
done
echo "PASS all console scripts installed and --help exits 0"
"$VENV/bin/bioheaders" --version
"$VENV/bin/fhr-validate" "$EX/minimal.fhr.json"
"$VENV/bin/fhr-fasta-validate" "$EX/example.fhr.fasta"
"$VENV/bin/python" -W error -c "import bioheaders" && echo "PASS import bioheaders under -W error"
"$VENV/bin/python" -W always -c "import warnings,sys
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter('always')
    import fhr
dep=[x for x in w if issubclass(x.category, DeprecationWarning)]
assert len(dep)==1, [str(x.message) for x in w]
print('PASS import fhr: exactly one DeprecationWarning:', dep[0].message)"
"$VENV/bin/python" -c "import bioheaders, os; print('installed at', os.path.dirname(bioheaders.__file__))"
