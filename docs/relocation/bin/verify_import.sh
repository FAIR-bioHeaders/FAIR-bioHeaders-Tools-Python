#!/usr/bin/env bash
# usage: verify_import.sh <tools-mirror.git> <cut-sha> <imported-repo> <commit-map>
# Checks: (1) the imported main tree equals the cut tree minus the Tools-only
# exclusions, byte-for-byte (mode + blob ID + path); (2) commit-map covers every
# commit reachable from the cut; (3) imported main maps from the cut SHA;
# (4) no tags or other refs in the imported repo; (5) authorship/dates preserved.
set -euo pipefail
export LC_ALL=C
SRC=$1 CUT=$2 DST=$3 MAP=$4
EXCL='^(galaxy/|\.github/workflows/galaxy-tools\.yml$|tests/galaxy_metadata_tool_test\.py$)'
git -C "$SRC" -c core.quotepath=off ls-tree -r "$CUT" | awk -F'\t' -v OFS='\t' '{split($1,a," "); print a[1]" "a[3], $2}' \
  | grep -Pv "\t$(echo "$EXCL" | sed 's/^\^//')" | sort -t$'\t' -k2 > /tmp/vi_expected.txt || true
git -C "$SRC" -c core.quotepath=off ls-tree -r "$CUT" | cut -f2 | grep -E "$EXCL" > /tmp/vi_excluded.txt || true
git -C "$DST" -c core.quotepath=off ls-tree -r main | awk -F'\t' -v OFS='\t' '{split($1,a," "); print a[1]" "a[3], $2}' | sort -t$'\t' -k2 > /tmp/vi_actual.txt
echo "expected kept files: $(wc -l < /tmp/vi_expected.txt); excluded: $(wc -l < /tmp/vi_excluded.txt); imported files: $(wc -l < /tmp/vi_actual.txt)"
if diff -u /tmp/vi_expected.txt /tmp/vi_actual.txt; then echo "PASS 1 tree: every kept path has identical mode and blob ID; nothing extra"; else echo "FAIL 1 tree"; exit 1; fi
n_src=$(git -C "$SRC" rev-list --count "$CUT")
n_map=$(tail -n +2 "$MAP" | wc -l)
n_pruned=$(tail -n +2 "$MAP" | awk '$2 ~ /^0+$/' | wc -l)
n_dst=$(git -C "$DST" rev-list --count main)
missing=$(comm -23 <(git -C "$SRC" rev-list "$CUT" | sort) <(tail -n +2 "$MAP" | cut -d' ' -f1 | sort) | wc -l)
echo "source commits: $n_src; commit-map rows: $n_map; pruned (became empty): $n_pruned; imported commits: $n_dst; unmapped: $missing"
[ "$missing" -eq 0 ] && [ $((n_map - n_pruned)) -eq "$n_dst" ] && echo "PASS 2 commit-map covers every source commit" || { echo "FAIL 2 commit-map"; exit 1; }
head_new=$(awk -v c="$CUT" '$1==c{print $2}' "$MAP")
[ "$head_new" = "$(git -C "$DST" rev-parse main)" ] && echo "PASS 3 cut $CUT -> import head $head_new" || { echo "FAIL 3 head mapping"; exit 1; }
refs=$(git -C "$DST" for-each-ref --format='%(refname)' | grep -v '^refs/heads/' || true)
tags=$(git -C "$DST" tag | wc -l)
[ -z "$refs" ] && [ "$tags" -eq 0 ] && echo "PASS 4 no tags or non-branch refs" || { echo "FAIL 4 refs: $refs"; exit 1; }
bad=0
while read -r o n; do
  [[ $n =~ ^0+$ ]] && continue
  [ "$(git -C "$SRC" log -1 --format='%an|%ae|%aD|%cn|%ce|%cD' "$o")" = "$(git -C "$DST" log -1 --format='%an|%ae|%aD|%cn|%ce|%cD' "$n")" ] || bad=$((bad+1))
done < <(tail -n +2 "$MAP")
[ "$bad" -eq 0 ] && echo "PASS 5 author/committer names, emails and dates preserved on every imported commit" || { echo "FAIL 5 ($bad commits differ)"; exit 1; }
