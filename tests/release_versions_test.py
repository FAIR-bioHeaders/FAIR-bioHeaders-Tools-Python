# SPDX-License-Identifier: MPL-2.0
"""Release preflight refuses inconsistent independent metadata holders."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip(
    "tomllib", reason="release preflight uses Python 3.11+; CI runs it on 3.13"
)
SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_release_versions.py"


@pytest.fixture
def release(tmp_path):
    files = {
        "pyproject.toml": '[tool.poetry]\nversion="1.2.3"\n',
        "compat/fhr/pyproject.toml": '[project]\nversion="1.2.3"\ndependencies=["fair-bioheaders==1.2.3"]\n',
        "bioheaders/__init__.py": '__version__ = "1.2.3"\n',
        "plugins/fair-bioheaders/.claude-plugin/plugin.json": json.dumps(
            {"version": "1.2.3"}
        ),
        "CITATION.cff": "version: 1.2.3\ndate-released: 2026-11-19\n",
        "CHANGELOG.md": "## 1.2.3 (2026-11-19)\n",
        "README.md": "**1.2.3**, current toolkit\n",
    }
    for name, value in files.items():
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(value)
    return tmp_path


def invoke(root, tag="v1.2.3"):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), "--tag", tag],
        capture_output=True,
        text=True,
    )


def test_coherent_release_passes(release):
    result = invoke(release)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "name",
    [
        "compat/fhr/pyproject.toml",
        "bioheaders/__init__.py",
        "plugins/fair-bioheaders/.claude-plugin/plugin.json",
        "CITATION.cff",
        "CHANGELOG.md",
        "README.md",
    ],
)
def test_one_stale_holder_blocks_publication(release, name):
    target = release / name
    target.write_text(target.read_text().replace("1.2.3", "1.2.2"))
    assert invoke(release).returncode == 1


def test_compatibility_dependency_cannot_float(release):
    target = release / "compat/fhr/pyproject.toml"
    target.write_text(target.read_text().replace("==1.2.3", ">=1.2.3"))
    assert invoke(release).returncode == 1


def test_wrong_tag_cannot_reuse_other_version(release):
    assert invoke(release, "v1.2.4").returncode == 1


def test_missing_holder_fails_closed(release):
    (release / "CITATION.cff").unlink()
    assert invoke(release).returncode == 1


def test_citation_date_must_be_a_calendar_date(release):
    target = release / "CITATION.cff"
    target.write_text(target.read_text().replace("2026-11-19", "2026-02-30"))
    assert invoke(release).returncode == 1


def test_galaxy_wrappers_are_not_a_holder(release):
    """The Galaxy wrappers stay in FAIR-bioHeaders-Tools (decision 29), so a
    checkout without galaxy/, or with a stale copy, does not affect the preflight."""
    assert not (release / "galaxy").exists()
    assert invoke(release).returncode == 0
    stale = release / "galaxy/tools/fair_bioheaders/macros.xml"
    stale.parent.mkdir(parents=True)
    stale.write_text('<macros><token name="@TOOL_VERSION@">0.0.1</token></macros>')
    assert invoke(release).returncode == 0


@pytest.mark.parametrize("quote", ["'", '"'])
def test_quoted_citation_dates_are_allowed(release, quote):
    target = release / "CITATION.cff"
    target.write_text(
        target.read_text().replace("2026-11-19", quote + "2026-11-19" + quote)
    )
    assert invoke(release).returncode == 0
