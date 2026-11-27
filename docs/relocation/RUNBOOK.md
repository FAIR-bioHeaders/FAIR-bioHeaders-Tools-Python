# Runbook: history-preserving import of the Python toolkit into FAIR-bioHeaders-Tools-Python (0.14.0 relocation, step S2)

Authority: specification#296 implementation instruction (2026-11-26, item 2);
Tools#206 design record D2/D4/D6 and "Maintainer decisions recorded"
(decisions 1, 2, 25, 29); Tools#211; Tools-Python#1, #2, #4.

Prepared and rehearsed locally on 2026-11-26. Nothing in this runbook was pushed
by an agent. The one push in step 7 is a human action (David or Adam), because it
creates the default branch of an empty repository and cannot be a PR.

| Item | Value |
| --- | --- |
| Source | `https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Tools`, branch `main` |
| Cut SHA | `c7abb7358bbe09796051caa663000cd43bd605f6` (Merge PR #216, the receipt block; latest release v0.13.1). First prepared at `1f3cf7c28b3a52469a35148b566deb683712cc87` (PR #201); re-cut on 2026-11-26 after #216 merged. |
| Destination | `https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Tools-Python` (empty; `pypi` environment with reviewers and `v*` tag ruleset 28108406 already applied) |
| Tool | `git-filter-repo` 2.47.0 (PyPI), git 2.53.0, Python 3.13 |
| Path list | `python-paths.txt` (122 entries; 746 of the 789 files at the cut; 43 Galaxy-owned files stay in Tools) |
| Expected import head | `bfd73ddc6d6037f9842f4bb95d4ebaf2fab72dc9` (387 commits; reproduced twice from fresh mirrors with a byte-identical commit-map) |

Files next to this runbook (`~/.cache/p14impl/relocate/`):

- `python-paths.txt` — the path list passed to filter-repo.
- `bin/check_paths.py` — checks the path list against the cut (every current entry exists at the cut, every historical entry existed in history, every path ever in Tools history is either kept or explicitly Tools-only).
- `bin/verify_import.sh` — tree/blob, commit-map, head mapping, refs and authorship checks.
- `bin/compare_dists.py` — member-by-member wheel/sdist comparison.
- `bin/smoke_installed.sh` — installed-package checks outside the checkout.
- `tools-python/` — the rehearsed import (branch `main` = expected import head; branch `relocation-0.14.0` = the drafted follow-up PR).
- `logs/` — verification logs from the rehearsal.

The same runbook, path list, scripts and commit-map are carried into Tools-Python by the follow-up PR under `docs/relocation/`, which is how the provenance is published (D2).

## 0. Preconditions (human, before step 1)

1. Name the maintainer doing the push on Tools-Python#1 (decision 4: David or Adam).
2. Announce the Python freeze in Tools (D6 step 2): from the cut until Tools-Python CI is green, no Python PR merges in Tools.
3. Confirm the cut is still current and nothing is open that would be lost:

   ```bash
   gh api repos/FAIR-bioHeaders/FAIR-bioHeaders-Tools/commits/main -q .sha
   # must print c7abb7358bbe09796051caa663000cd43bd605f6; if not, see "If Tools main moved" below
   gh pr list -R FAIR-bioHeaders/FAIR-bioHeaders-Tools --state open
   gh api repos/FAIR-bioHeaders/FAIR-bioHeaders-Tools-Python/git/trees/main 2>&1 | grep -q "Git Repository is empty" && echo "destination empty"
   ```

   Any PR open at the cut that touches Python paths is recreated against Tools-Python after the import with a back-link; nothing is force-pushed.

**If Tools main moved.** Record the new HEAD as the cut SHA, substitute it everywhere below, rerun step 3 (`check_paths.py`) and regenerate section 8 of `python-paths.txt` if new paths appeared or were renamed. The expected import head then changes; record the new one from step 4. Do not reuse `bfd73ddc`.

## 1. Workspace and filter-repo

```bash
export WORK=~/.cache/p14impl/relocate          # any empty directory with ~200 MB free
export CUT=c7abb7358bbe09796051caa663000cd43bd605f6
cd "$WORK"
python3 -m venv .venv-fr || uv venv -p python3.13 .venv-fr   # rehearsal used uv (no ensurepip on the host)
.venv-fr/bin/python -m pip install git-filter-repo==2.47.0 || uv pip install -p .venv-fr/bin/python git-filter-repo==2.47.0
.venv-fr/bin/git-filter-repo --version          # rehearsal: a40bce548d2c (2.47.0)
```

## 2. Fresh mirror at the cut

```bash
rm -rf import.git
git clone --mirror https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Tools.git import.git
test "$(git -C import.git rev-parse refs/heads/main)" = "$CUT" && echo "cut confirmed"
```

## 3. Check the path list

```bash
python3 -I bin/check_paths.py import.git "$CUT" python-paths.txt
# expected: entries=122 cut_files=789 kept_at_cut=746 excluded_at_cut=43 history_paths=877 problems=0
```

## 4. Rewrite (history preserved, `main` only, no tags)

```bash
cd "$WORK/import.git"
"$WORK/.venv-fr/bin/git-filter-repo" --paths-from-file "$WORK/python-paths.txt" --refs main
git rev-parse main                       # expected bfd73ddc6d6037f9842f4bb95d4ebaf2fab72dc9
cp filter-repo/commit-map "$WORK/commit-map.txt"
cd "$WORK"
rm -rf tools-python
git clone --single-branch --branch main --no-tags import.git tools-python
git -C tools-python remote remove origin
```

Notes on the rewrite:

- `--refs main` rewrites only `main`. The mirror's tags and `refs/pull/*` are left untouched in `import.git` and are never cloned into `tools-python` (`--single-branch --no-tags`), so **no tag is imported**; v0.3.x–v0.13.x stay in Tools (D2).
- Three commits touched only Galaxy-owned paths and become empty, so filter-repo prunes them (their commit-map rows map to `0000…`): `094e35b` (#115), `3b38fb1` (#138) and `eb554ac`. They stay in Tools with the Galaxy history.
- filter-repo's default rewrites abbreviated hashes of *kept* commits inside commit messages to their new IDs. In the rehearsal this changed exactly four messages, all genuine commit references (`b09ebb9`, `1d992a8`, `fdc9677`, `729561b` → their new IDs). Hashes of pruned commits and hex-looking numbers that are not kept commits (for example `6762547`) are left as-is (`filter-repo/suboptimal-issues`). Every other message, author, committer and date is unchanged.
- Known, accepted limitation: commit messages keep their original `#N` references, which mean Tools issues/PRs. On GitHub, Tools-Python will autolink them to its own numbers (#1–#4 exist today). The commit-map and the `docs/relocation/` record say so; messages are not rewritten.

## 5. Import verification (agent or maintainer)

```bash
cd "$WORK"
git clone --mirror https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Tools.git tools-mirror.git   # untouched reference copy
bin/verify_import.sh tools-mirror.git "$CUT" tools-python commit-map.txt
for f in bioheaders/__init__.py fhr.py tests/fhr_test.py; do
  echo "$f import=$(git -C tools-python log --follow --format=%h -- $f | wc -l) tools=$(git -C tools-mirror.git log main --follow --format=%h -- $f | wc -l)"
done
```

Expected: PASS 1–5 (746 kept files with identical mode and blob ID and nothing extra; 390 source commits all in the commit-map, 3 pruned, 387 imported; cut → `bfd73ddc`; no tags or other refs; authorship and dates preserved), and equal `--follow` counts (64, 44, 49).

## 6. Pre-push verification checklist

All checks run against `tools-python` at the import head, from installed artifacts outside the checkout where the item says so. A missing, failed or NOT_RUN item blocks the push unless this runbook records why it cannot run locally and which CI job covers it.

```bash
cd "$WORK"
# test environment, as in .github/workflows/pytest.yaml
uv venv --seed -p python3.13 venv-py313          # or: python3.13 -m venv venv-py313
export VIRTUAL_ENV=$WORK/venv-py313 PATH=$WORK/venv-py313/bin:$PATH
pip install poetry==2.3.2 build==1.6.1
(cd tools-python && poetry install && pip install --no-deps . && pip install pysam)
# pinned specification and draft suites, as in pytest.yaml
git clone --depth 1 --branch v0.8.0 https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification.git spec
test "$(git -C spec rev-parse HEAD)" = 72cb46b98160ecc7a7f20ef579a6879d5030c40b
git -C spec fetch --depth 1 origin '+refs/tags/*:refs/tags/*'
for F in FHT FHGM; do
  rev=$(python3 -c "import json; print(json.load(open('tools-python/bioheaders/schemas/bundled.json'))['drafts']['$F']['suite']['revision'])")
  git init -q $F-Specification && git -C $F-Specification fetch -q --depth 1 https://github.com/FAIR-bioHeaders/$F-Specification.git $rev && git -C $F-Specification checkout -q FETCH_HEAD
done
```

| # | Check | Command (from `$WORK`) | Pass condition |
| --- | --- | --- | --- |
| 6.1 | `pip install` from the result | `bin/smoke_installed.sh $WORK/venv-smoke-git $WORK/tools-python/examples $WORK/ref-ep/entry_points.txt "git+file://$WORK/tools-python@main"` | installs; 13 console scripts identical to 0.13.1 (the `fhr` distribution is not installed by this route, so its line is expected to stop with `PackageNotFoundError: fhr`) |
| 6.2 | Full test suite (main CI job) | `(cd tools-python && FHR_REQUIRE_SPECIFICATION=1 FHR_SPECIFICATION=$WORK/spec pytest -rs)` | same pass/skip/fail counts as the same command on a Tools checkout at `$CUT`; no failures |
| 6.3 | FHT and FHGM conformance jobs | `(cd tools-python && BIOHEADERS_EXPERIMENTAL_FHT=1 FHT_REQUIRE_SUITE=1 FHT_SPECIFICATION=$WORK/FHT-Specification pytest -rs tests/fht_conformance_test.py)` and `(cd tools-python && BIOHEADERS_EXPERIMENTAL_FHGM=1 FHGM_REQUIRE_SUITE=1 FHGM_SPECIFICATION=$WORK/FHGM-Specification pytest -rs tests/fhgm_conformance_test.py tests/fhgm_native_conformance_test.py)` | all pass |
| 6.4 | Lint, format, types, matrix | `(cd tools-python && ruff check . && isort . --check-only && black . --check && mypy -p bioheaders && python scripts/render_capability_matrix.py --suite ../spec/conformance --check --self-test)` | all pass; matrix render matches |
| 6.5 | CLI entry points identical to 0.13.1 | download the four 0.13.1 files from PyPI into an empty `pypi-0.13.1/` (sha256 `9f600347…` wheel, `32a41145…` sdist, `cc3edcbe…` fhr wheel, `2e52c7d5…` fhr sdist); extract `fair_bioheaders-0.13.1.dist-info/entry_points.txt` to `ref-ep/`; `bin/smoke_installed.sh $WORK/venv-smoke-wheel $WORK/tools-python/examples $WORK/ref-ep/entry_points.txt build-out/*.whl` | 13 names and targets identical; `fhr` declares the same 11 `fhr-*`; every command `--help` exits 0; release.yml smoke commands pass; `import bioheaders` clean under `-W error`; `import fhr` emits exactly one DeprecationWarning |
| 6.6 | `python -m build` sdist/wheel vs 0.13.1 PyPI | `python -m build tools-python --outdir build-out && python -m build tools-python/compat/fhr --outdir build-out`; build the Tools cut the same way into `build-cut/`; then `python3 -I bin/compare_dists.py build-cut/X build-out/X` and `python3 -I bin/compare_dists.py pypi-0.13.1/X build-out/X` for each of the four files | import vs cut: identical members and bytes (all four). Import vs PyPI 0.13.1: identical member names; `fhr` wheel and sdist byte-identical per member; `fair-bioheaders` differs only in the files changed on Tools `main` after v0.13.1 (`git diff --name-only v0.13.1 $CUT -- bioheaders README.md pyproject.toml`: 11 files, the unreleased #197 `metadata --json` and Round 16 fixes) plus generated metadata (`METADATA`/`PKG-INFO` from README, `RECORD`, and `WHEEL` `Generator: poetry-core` 2.5.0 vs 2.3.1, which also adds a `Python :: 3.15` classifier — reproduced by rebuilding the v0.13.1 tag itself) |
| 6.7 | Licence and provenance | `git -C tools-python rev-parse main:LICENSE main:compat/fhr/LICENSE` and `git -C tools-mirror.git rev-parse $CUT:LICENSE`; `git -C tools-python ls-tree -r --name-only main \| grep -c '^galaxy/'`; inspect wheel `dist-info/licenses/LICENSE` and `License:` metadata | all three LICENSE blobs `2e942bbd…` (D9 byte-identical); 0 Galaxy (MIT) files imported; wheel ships LICENSE with `License: MPL-2.0`; first commit `883ca80 2022-03-31 David Molik Initial commit` present, so `LICENSE:24` "version history identify provenance" stays true |
| 6.8 | Release preflight | `(cd tools-python && python scripts/check_release_versions.py)` | **Expected to fail at the import head** (`galaxy/tools/fair_bioheaders/macros.xml` is Tools-only after decision 29). Not a push blocker: the follow-up PR removes the Galaxy holder (eight → seven holders) before CI is relied on. Recorded so nobody mistakes it for an import defect. |

### 6.x Rehearsal results (2026-11-26, this machine; logs in `logs/`)

| # | Result |
| --- | --- |
| re-cut | Tools main moved to `c7abb735` (#216: `.github/pull_request_template.md` added — now carried — and AGENTS.md). Steps 2–6 rerun: path-list check 0 problems; import head `bfd73ddc` (old head `b3b55df0` is its ancestor; the 387 commits up to it are unchanged), reproduced from a second mirror with a byte-identical commit-map; verify_import PASS 1–5; full suite 3557 passed / 392 skipped / 0 failed (unchanged); follow-up branch rebased cleanly, 3555 / 392 / 0. Packaged files are unchanged by #216, so the build, entry-point and licence results below carry over. |
| 5 | PASS 1–5 (re-cut): 746/746 files identical mode+blob, 43 Galaxy files excluded, nothing extra; 390 commits mapped (387 imported, 3 pruned); cut → `bfd73ddc`; no tags/refs; authorship/dates identical. `--follow` 64/44/49 = Tools. Re-run from a second fresh mirror: same head, byte-identical commit-map. |
| 6.1 | PASS (`git+file` install; 13 console scripts identical). |
| 6.2 | PASS. Python 3.13: import 3557 passed / 392 skipped / 0 failed; Tools cut, same command and environment: 3574 / 391 / 0. Difference fully explained: 16 `tests/galaxy_metadata_tool_test.py` cases stay in Tools; `fhr1_compat_test::test_old_toolkit_examples_still_validate` skips because the `v0.3.1` tag is not imported (it already skips in Tools CI, whose checkout has no tags) — with a temporary local tag on the mapped commit `4e574398` it passes, and the three v0.3.1 example blobs are identical. Python 3.9: 3473 passed / 460 skipped / 1 failed — `fhgff3_microdata_test::test_installed_distribution_round_trip` fails at `ensurepip` inside a nested venv of the local uv-built CPython 3.9; the **same test fails identically on the Tools cut** in that environment, so it is environmental (CI uses actions/setup-python). |
| 6.2 NOT_RUN locally | `tests/faidx_test.py` samtools/bgzip comparisons (4 skips): samtools/bgzip are not installed here and installing them was not permitted in this session; `FHR_REQUIRE_FAIDX_TOOLS=1` was therefore not set. The pysam comparison ran. Covered by Tools-Python `pytest.yaml` (installs samtools/tabix, sets the variable). `FHR_MEMORY_TEST` (2 skips) is opt-in in CI too. |
| 6.3 | PASS. FHT 104 passed / 83 skipped (vectors without parent files); FHGM 372 passed. |
| 6.4 | PASS (ruff, isort, black, mypy 35 files; matrix 245 cells / 247 probes, self-test 11/11). |
| 6.5 | PASS for wheel and sdist installs. |
| 6.6 | PASS. Import vs cut: 0 differing members in all four artifacts. Import vs PyPI 0.13.1: same member names; `fhr` wheel/sdist 0 differing; `fair-bioheaders` wheel 13 / sdist 13 differing = the 10 `bioheaders/*.py` + README/pyproject changed after v0.13.1 (PRs #203, #201) + generated metadata. Rebuilding the v0.13.1 tag gives only the poetry-core generator/classifier differences, so the build itself is reproducible. |
| 6.7 | PASS (LICENSE ×3 = `2e942bbd`; 0 Galaxy files; `License: MPL-2.0`; history from `883ca80` 2022-03-31). Note, unchanged from PyPI 0.13.1: the `fhr` wheel's metadata says `License: FAIR-bioHeaders-Tools` (setuptools takes the first line of `license = {file = "LICENSE"}`); not altered here. |
| 6.8 | Expected FAIL at the import head (Galaxy holder); PASS on the follow-up branch. |
| advisory | `declared-references.yml`, `pin-audit.yml` (network-dependent, advisory, untouched by the import) and `codacy.yml` (needs the `CODACY_PROJECT_TOKEN` secret in Tools-Python): NOT_RUN locally. `galaxy-tools.yml` is not imported. |

## 7. The one-time push (human: David or Adam)

Run only after steps 5 and 6 are recorded on Tools#206/Tools-Python#1. It pushes exactly the verified commit to `main`, nothing else (no tags, no other branch):

```bash
git -C ~/.cache/p14impl/relocate/tools-python push --no-follow-tags https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Tools-Python.git bfd73ddc6d6037f9842f4bb95d4ebaf2fab72dc9:refs/heads/main
```

Immediately afterwards:

```bash
git ls-remote https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Tools-Python.git
# expected: exactly one ref, refs/heads/main bfd73ddc6d6037f9842f4bb95d4ebaf2fab72dc9 (plus HEAD); no tags
gh api repos/FAIR-bioHeaders/FAIR-bioHeaders-Tools-Python -q .default_branch     # main
```

If the push went wrong (wrong commit, extra refs): do not build on it. An admin deletes the extra refs or force-resets `main` to the verified SHA once, and the event is recorded on Tools-Python#1. Tools itself is never changed by this step, so the rollback source is Tools `main` at `$CUT` (D6).

Pushing the workflows activates `pytest.yaml` and friends on `main` in Tools-Python. The first `pytest.yaml` run on `main` is expected to fail at "Preflight release versions" (6.8) until the follow-up PR merges. `release.yml` and `container.yml` only run on `v*.*.*` tags, which the ruleset restricts to admins; no tag exists.

## 8. After the push

1. Agent: rerun `bin/verify_import.sh` against a fresh clone of Tools-Python and post the result on Tools-Python#1 (D6 step 2).
2. Agent: push the drafted branch `relocation-0.14.0` (already in `tools-python`) to a feature branch and open the follow-up PR (draft contents: version 0.14.0, CHANGELOG relocation entry, Tools-Python URLs, release workflow with explicit PEP 740 attestations, Galaxy holder removed from the release preflight, `.zenodo.json`, and `docs/relocation/` with this runbook, the path list, scripts and `commit-map.txt`). Independent model review, human merge.
3. Human: PyPI trusted publishers for `fair-bioheaders` and `fhr` → repository `FAIR-bioHeaders/FAIR-bioHeaders-Tools-Python`, workflow `release.yml`, environment `pypi`; GHCR package `fair-bioheaders` grants Tools-Python Actions write access; Zenodo steps below.
4. Then the 0.14.0 relocation release (separate step, D6 step 4), verified through PyPI, Bioconda and GHCR before any Tools cleanup.

## 9. Zenodo (decision 1) — maintainer steps

Goal: the existing "FHR File Converter" concept `10.5281/zenodo.6762547` stays as it is and citable; Tools-Python gets a **new concept DOI** linked to it with `isNewVersionOf` (new → old) and `isContinuedBy` (old → new); the Tools GitHub auto-deposit is separated so that no Tools GitHub Release (Rust) ever becomes an "FHR File Converter" version.

Who: the Zenodo account that owns concept 6762547 (it controls the Tools GitHub hook), David or Adam, named on Tools-Python#4.

A. Separate the old Tools auto-deposit (before any GitHub Release in Tools, and before the 0.14.0 tag):
1. Sign in at https://zenodo.org with the owning account → avatar menu → **GitHub** (https://zenodo.org/account/settings/github/).
2. Find `FAIR-bioHeaders/FAIR-bioHeaders-Tools` and switch its toggle **Off**. This removes Zenodo's webhook; published records are unaffected.
3. Verify on GitHub: `gh api repos/FAIR-bioHeaders/FAIR-bioHeaders-Tools/hooks -q '.[].config.url'` shows no `zenodo.org` URL (needs admin on the repository).

B. Enable Tools-Python (before the 0.14.0 tag):
1. On the same Zenodo GitHub page, press **Sync now**. If `FAIR-bioHeaders-Tools-Python` does not appear, grant the Zenodo OAuth app access to the FAIR-bioHeaders organisation (GitHub → Settings → Applications → Authorized OAuth Apps → Zenodo → Organization access → Grant/Request).
2. Switch `FAIR-bioHeaders/FAIR-bioHeaders-Tools-Python` **On**.
3. The follow-up PR adds `.zenodo.json` (Zenodo reads it instead of `CITATION.cff`). It declares `upload_type: software`, the creators, `license: MPL-2.0` and `related_identifiers: [{"identifier": "10.5281/zenodo.6762547", "relation": "isNewVersionOf", "resource_type": "software", "scheme": "doi"}]`, so the new record carries the forward relation from its first deposit. Check that the file is on `main` before tagging.

C. At the 0.14.0 release:
1. The `github-release` job publishes the GitHub Release; Zenodo then creates a **new concept DOI** and the v0.14.0 version DOI. Record both from the record page (the "Cite all versions" DOI is the concept).
2. Check the new record's **Related works** shows "Is new version of 10.5281/zenodo.6762547". If `.zenodo.json` was not used or the relation is missing: Edit → Related works → Add: Relation **Is new version of**, Identifier `10.5281/zenodo.6762547`, Scheme DOI, Resource type Software → **Publish**.

D. Link the old record forward (after C):
1. Open the latest old version record https://zenodo.org/records/24387470 (v0.13.1) → **Edit** (metadata edits do not create a new version).
2. Related works → Add: Relation **Is continued by**, Identifier = the new Tools-Python **concept** DOI, Scheme DOI, Resource type Software → **Publish**.
   API equivalent (personal token with `deposit:write` and `deposit:actions`):
   ```bash
   T=<token>; R=24387470
   curl -sS -X POST -H "Authorization: Bearer $T" https://zenodo.org/api/records/$R/draft
   curl -sS -H "Authorization: Bearer $T" https://zenodo.org/api/records/$R/draft > draft.json
   # append to .metadata.related_identifiers:
   #   {"identifier": "<new concept DOI>", "scheme": "doi", "relation_type": {"id": "iscontinuedby"}, "resource_type": {"id": "software"}}
   curl -sS -X PUT -H "Authorization: Bearer $T" -H "Content-Type: application/json" --data @draft-edited.json https://zenodo.org/api/records/$R/draft
   curl -sS -X POST -H "Authorization: Bearer $T" https://zenodo.org/api/records/$R/draft/actions/publish
   ```
3. Confirm with `curl -s https://zenodo.org/api/records/24387470 | python3 -m json.tool | grep -A3 iscontinuedby` and the matching `isnewversionof` on the new record. Zenodo shows relations per record, not per concept; that is expected (decision record: "how the two relation types appear on each record" was to be confirmed — record what is displayed).

E. Record: post both new DOIs on Tools-Python#4 and specification#299; a follow-up Tools-Python PR adds the new concept DOI to `CITATION.cff` identifiers and the README badge (keeping 6762547 for historical versions); bio.tools, Bioconda `extra.identifiers` and the website resources check add the new concept at S4 (Tools#211 A5). The Rust core gets its own concept at its first GitHub Release from Tools, which requires A to be done first.
