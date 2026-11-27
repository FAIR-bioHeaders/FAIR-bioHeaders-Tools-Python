# Relocation record: FAIR-bioHeaders-Tools → FAIR-bioHeaders-Tools-Python (0.14.0)

This repository was created from
[FAIR-bioHeaders-Tools](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Tools)
by a history-preserving import, following the
[Tools#206 design record](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Tools/issues/206#issuecomment-7172928109)
(D2) and the
[maintainer decisions](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Tools/issues/206#issuecomment-7173759404),
under the implementation instruction on
[specification#296](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/issues/296).
FAIR-bioHeaders-Tools keeps its own history, tags and releases unchanged; nothing
there was rewritten.

| Item | Value |
| --- | --- |
| Source | FAIR-bioHeaders-Tools `main` |
| Cut commit | `c7abb7358bbe09796051caa663000cd43bd605f6` (Merge PR #216; the last release from there is v0.13.1) |
| Import head here | `bfd73ddc6d6037f9842f4bb95d4ebaf2fab72dc9` |
| Tool | git-filter-repo 2.47.0, git 2.53.0 |
| Command | `git filter-repo --paths-from-file python-paths.txt --refs main` on a fresh `git clone --mirror`, then `git clone --single-branch --branch main --no-tags` |
| Path list | [`python-paths.txt`](python-paths.txt) (122 entries) |
| Commit map | [`commit-map.txt`](commit-map.txt): every one of the 390 source commits → its commit here (`0000…` = pruned) |
| Tag locations | [`tag-map.txt`](tag-map.txt): the commit here for each Tools release tag. Tags were **not** imported. |
| Runbook | [`RUNBOOK.md`](RUNBOOK.md), with the scripts in [`bin/`](bin/) |

## What was carried and what stayed

Carried: everything under the Python toolkit's ownership in Tools#206 D4 — the
`bioheaders` package (including its own copies of the frozen assessment schemas in
`bioheaders/assess/data/`), the `fhr` compatibility module, shims and
distribution, tests and fixtures, examples, documentation, scripts, specs, the
Claude Code plugin and a copy of its marketplace manifest, packaging and container
files, the Python workflows and the PR template (with the Project 14 receipt block), and the repository files (LICENSE byte-identical).
Historical names of these paths (the pre-0.4.0 `lib/`, `src/`,
`fhr_file_converter/`, `t/` layouts and the removed `nextflow/` tree) are included
so that history before renames survives.

Stayed only in FAIR-bioHeaders-Tools (decision 29): `galaxy/`,
`.github/workflows/galaxy-tools.yml` and `tests/galaxy_metadata_tool_test.py`.
Three commits that changed only those paths became empty and were pruned:
Tools `094e35b` (#115), `3b38fb1` (#138) and `eb554ac`.

FAIR-bioHeaders-Tools also keeps byte-identical copies at the raw `main` URLs of
the three assessment schemas, whose `$id`s point there (decision 25), and the
`.claude-plugin/marketplace.json` install address.

## Verification at import

- The tree at the import head equals the Tools tree at the cut minus the 43
  Galaxy-owned files: identical mode and blob ID for all 746 files, nothing extra.
- The commit map covers all 390 commits reachable from the cut (387 imported,
  3 pruned); authors, committers and dates are unchanged on every imported commit;
  `git log --follow` gives the same history length for `bioheaders/__init__.py`
  (64), `fhr.py` (44) and `tests/fhr_test.py` (49).
- The import is deterministic: two runs from fresh mirrors gave the same head and
  a byte-identical commit map.
- Built wheels and sdists are member-for-member identical to builds of the Tools
  cut; the 13 console scripts are identical to 0.13.1 on PyPI.

## Notes for readers of the history

- Commit messages are unchanged except that filter-repo rewrote four abbreviated
  references to kept commits (`b09ebb9`, `1d992a8`, `fdc9677`, `729561b`) to their
  new IDs. Other hashes in messages refer to FAIR-bioHeaders-Tools; look them up in
  `commit-map.txt`.
- `#N` in messages before the import refers to FAIR-bioHeaders-Tools issues and
  PRs, even where GitHub links it to this repository.
- Tests that read release tags from Git (for example the v0.3.1 examples in
  `tests/fhr1_compat_test.py`) skip here because the tags stayed in Tools; the
  same files are at the commit given for `v0.3.1` in `tag-map.txt`.
