"""Validates that tracks/*/track.yaml reference only files that exist.

Nothing else in the codebase checks that a persona / question_banks / domain_packs /
calibration / catalog path in a track.yaml resolves to a real file — that's exactly the
class of bug that let the data-ai-leadership track's platform_architecture and
ai_governance phases ship pointing at missing files. Run with
`uv run pytest tests/test_track_yaml.py -v` from mcp/.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
TRACKS_DIR = REPO_ROOT / "tracks"
CATALOGS_DIR = REPO_ROOT / "mcp" / "data" / "catalogs"

TRACK_FILES = sorted(TRACKS_DIR.glob("*/track.yaml"))


def _load(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text())


def _resolve(path_str: str) -> Path:
    return REPO_ROOT / path_str


@pytest.fixture(params=TRACK_FILES, ids=[p.parent.name for p in TRACK_FILES])
def track(request: pytest.FixtureRequest) -> tuple[dict[str, Any], Path]:
    path: Path = request.param
    return _load(path), path


def test_track_has_phases(track: tuple[dict[str, Any], Path]) -> None:
    data, path = track
    assert data.get("phases"), f"{path}: no phases declared"


def test_top_level_paths_resolve(track: tuple[dict[str, Any], Path]) -> None:
    data, path = track
    for key in ("calibration", "calibration_overlay", "report_template"):
        value = data.get(key)
        if value is None:
            continue
        assert _resolve(value).is_file(), f"{path}: {key} -> {value!r} does not exist"

    for key in ("question_banks", "domain_packs"):
        for value in data.get(key) or []:
            assert _resolve(value).is_file(), f"{path}: top-level {key} entry {value!r} does not exist"


def test_no_singular_question_bank_key(track: tuple[dict[str, Any], Path]) -> None:
    data, path = track
    for phase in data.get("phases", []):
        assert "question_bank" not in phase, (
            f"{path}: phase {phase.get('id')!r} uses the singular 'question_bank' key — "
            "use the plural 'question_banks' list"
        )


def test_phase_paths_resolve(track: tuple[dict[str, Any], Path]) -> None:
    data, path = track
    for phase in data.get("phases", []):
        phase_id = phase.get("id")

        persona = phase.get("persona")
        if persona is not None:
            assert _resolve(persona).is_file(), f"{path}: phase {phase_id!r} persona -> {persona!r} does not exist"

        for qb in phase.get("question_banks") or []:
            assert _resolve(qb).is_file(), f"{path}: phase {phase_id!r} question_banks entry {qb!r} does not exist"

        catalog = phase.get("catalog")
        if catalog is not None:
            catalog_path = CATALOGS_DIR / f"{catalog}.json"
            assert catalog_path.is_file(), (
                f"{path}: phase {phase_id!r} catalog {catalog!r} -> {catalog_path} does not exist"
            )


def test_rubric_scored_by_phase_is_declared(track: tuple[dict[str, Any], Path]) -> None:
    data, path = track
    phase_ids = {p.get("id") for p in data.get("phases", [])}
    for dim in data.get("rubric", []):
        scored_by = dim.get("scored_by_phase")
        assert scored_by == "all" or scored_by in phase_ids, (
            f"{path}: rubric dimension {dim.get('id')!r} scored_by_phase {scored_by!r} "
            "is not 'all' or a declared phase id"
        )


def test_single_phase_scoring_keys_and_values_are_declared(track: tuple[dict[str, Any], Path]) -> None:
    data, path = track
    phase_ids = {p.get("id") for p in data.get("phases", [])}
    rubric_ids = {dim.get("id") for dim in data.get("rubric", [])}
    for phase_id, dims in (data.get("single_phase_scoring") or {}).items():
        assert phase_id in phase_ids, f"{path}: single_phase_scoring key {phase_id!r} is not a declared phase id"
        for dim_id in dims:
            assert dim_id in rubric_ids, (
                f"{path}: single_phase_scoring[{phase_id!r}] references undeclared rubric dimension {dim_id!r}"
            )
