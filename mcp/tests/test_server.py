"""Tests for the Cornerman MCP server.

Run with `uv run pytest` from mcp/. Each test gets an isolated on-disk
SQLite file via the `isolate_db` autouse fixture — none of these touch a
real ~/.cornerman/cornerman.db.
"""

import json
import sqlite3

import pytest

import server


@pytest.fixture(autouse=True)
def isolate_db(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "DB_PATH", tmp_path / "cornerman.db")
    yield


# ---------------------------------------------------------------------------
# _set_nested — dotted-path dossier merge
# ---------------------------------------------------------------------------


def test_set_nested_creates_intermediate_dicts():
    d: dict = {}
    server._set_nested(d, "a.b.c", "value")
    assert d == {"a": {"b": {"c": "value"}}}


def test_set_nested_merges_siblings_without_clobbering():
    d: dict = {"a": {"b": {"c": "value"}}}
    server._set_nested(d, "a.b.d", "value2")
    assert d["a"]["b"] == {"c": "value", "d": "value2"}


def test_set_nested_overwrites_leaf():
    d: dict = {"a": {"b": "old"}}
    server._set_nested(d, "a.b", "new")
    assert d["a"]["b"] == "new"


def test_coerce_value_parses_json_but_falls_back_to_raw_string():
    assert server._coerce_value('{"x": 1}') == {"x": 1}
    assert server._coerce_value("[1, 2, 3]") == [1, 2, 3]
    assert server._coerce_value("plain string") == "plain string"


# ---------------------------------------------------------------------------
# Session lifecycle
# ---------------------------------------------------------------------------


def test_session_lifecycle_end_to_end():
    started = server.session_start("candidate@example.com", "Head of Data", "data-ai-leadership")
    session_id = started["session_id"]
    assert session_id
    assert "created_at" in started

    server.session_update(session_id, "candidate.seniority", "staff")
    server.session_update(session_id, "target", json.dumps({"company": "Acme Mutual", "role": "Head of Data"}))

    got = server.session_get(session_id)
    assert got["track"] == "data-ai-leadership"
    assert got["candidate_id"] == "candidate@example.com"
    assert got["dossier"]["candidate"]["seniority"] == "staff"
    assert got["dossier"]["target"]["company"] == "Acme Mutual"
    assert got["rounds"] == []
    assert got["scores"] == []

    round_started = server.round_start(session_id, "hld", "design-a-payments-ledger", 60)
    assert round_started["phase"] == "hld"
    assert "auto_grade_at_iso" in round_started
    assert round_started["time_budget_minutes"] == 60

    round_ended = server.round_end(session_id, "hld")
    assert round_ended["session_id"] == session_id
    assert round_ended["phase"] == "hld"
    assert round_ended["overran"] in (True, False)

    saved = server.score_save(session_id, "hld", 4, "solid tradeoffs, weak on multi-region")
    assert saved == {"ok": True, "session_id": session_id, "dimension": "hld", "score": 4}

    listing = server.sessions_list("candidate@example.com")
    assert len(listing["sessions"]) == 1
    entry = listing["sessions"][0]
    assert entry["session_id"] == session_id
    assert entry["track"] == "data-ai-leadership"
    assert entry["scores"] == {"hld": 4}


def test_session_get_unknown_session_returns_error():
    result = server.session_get("does-not-exist")
    assert "error" in result


def test_session_update_unknown_session_returns_error():
    result = server.session_update("does-not-exist", "a.b", "value")
    assert "error" in result


def test_round_end_without_round_start_returns_error():
    session_id = server.session_start("candidate@example.com")["session_id"]
    result = server.round_end(session_id, "coding")
    assert "error" in result


def test_score_save_rejects_out_of_range_score():
    session_id = server.session_start("candidate@example.com")["session_id"]
    result = server.score_save(session_id, "coding", 9, "not a valid score")
    assert "error" in result


def test_session_start_track_defaults_to_empty_string():
    session_id = server.session_start("candidate@example.com")["session_id"]
    got = server.session_get(session_id)
    assert got["track"] == ""


# ---------------------------------------------------------------------------
# Migration — track column added to a pre-existing legacy schema
# ---------------------------------------------------------------------------


def test_migration_adds_track_column_without_losing_data(tmp_path, monkeypatch):
    legacy_db = tmp_path / "legacy.db"
    conn = sqlite3.connect(legacy_db)
    conn.execute(
        """
        CREATE TABLE sessions (
            id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL,
            target_role TEXT,
            created_at TEXT NOT NULL,
            dossier TEXT NOT NULL DEFAULT '{}'
        )
        """
    )
    conn.execute(
        "INSERT INTO sessions (id, candidate_id, target_role, created_at, dossier) VALUES (?, ?, ?, ?, ?)",
        (
            "legacy-session",
            "candidate@example.com",
            "Staff Backend Engineer",
            "2024-01-01T00:00:00+00:00",
            json.dumps({"candidate": {"seniority": "staff"}}),
        ),
    )
    conn.commit()
    conn.close()

    monkeypatch.setattr(server, "DB_PATH", legacy_db)

    conn = server._connect()
    try:
        cols = {row["name"] for row in conn.execute("PRAGMA table_info(sessions)")}
        assert "track" in cols

        row = conn.execute("SELECT * FROM sessions WHERE id = ?", ("legacy-session",)).fetchone()
        assert row["candidate_id"] == "candidate@example.com"
        assert row["target_role"] == "Staff Backend Engineer"
        assert row["track"] == ""
        assert json.loads(row["dossier"]) == {"candidate": {"seniority": "staff"}}
    finally:
        conn.close()

    # session_get (a real tool call) should also work against the migrated DB.
    got = server.session_get("legacy-session")
    assert got["track"] == ""
    assert got["dossier"]["candidate"]["seniority"] == "staff"


def test_migrate_is_safe_to_run_twice_against_same_connection(tmp_path, monkeypatch):
    """Simulates the race where two _connect() calls both see `track` missing
    before either ALTER TABLE commits — the second ALTER TABLE must not raise."""
    db_path = tmp_path / "race.db"
    monkeypatch.setattr(server, "DB_PATH", db_path)

    conn = server._connect()
    try:
        server._migrate(conn)  # second run against an already-migrated schema
        cols = {row["name"] for row in conn.execute("PRAGMA table_info(sessions)")}
        assert "track" in cols
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# pick_problem — catalog selection, tiers, exclusion
# ---------------------------------------------------------------------------


@pytest.fixture
def widgets_catalog(tmp_path, monkeypatch):
    catalogs_dir = tmp_path / "catalogs"
    catalogs_dir.mkdir()
    (catalogs_dir / "widgets.json").write_text(
        json.dumps(
            {
                "tier_difficulties": {"junior": ["easy"], "senior": ["hard"]},
                "problems": [
                    {"id": "w1", "difficulty": "easy", "name": "Widget One"},
                    {"id": "w2", "difficulty": "easy", "name": "Widget Two"},
                    {"id": "w3", "difficulty": "hard", "name": "Widget Three"},
                ],
            }
        )
    )
    monkeypatch.setattr(server, "CATALOGS_DIR", catalogs_dir)
    return catalogs_dir


def test_pick_problem_filters_by_tier_and_catalog(widgets_catalog):
    picked = server.pick_problem("junior", catalog="widgets")
    assert picked["id"] in {"w1", "w2"}
    assert picked["difficulty"] == "easy"

    picked_senior = server.pick_problem("senior", catalog="widgets")
    assert picked_senior["id"] == "w3"


def test_pick_problem_respects_exclude_ids(widgets_catalog):
    picked = server.pick_problem("junior", catalog="widgets", exclude_ids=["w1"])
    assert picked["id"] == "w2"


def test_pick_problem_exhausted_by_exclude_ids_returns_error(widgets_catalog):
    result = server.pick_problem("junior", catalog="widgets", exclude_ids=["w1", "w2"])
    assert "error" in result


def test_pick_problem_unknown_tier_for_catalog_returns_error(widgets_catalog):
    result = server.pick_problem("staff", catalog="widgets")
    assert "error" in result
    assert "staff" in result["error"]


def test_pick_problem_unknown_catalog_returns_error():
    result = server.pick_problem("junior", catalog="does-not-exist")
    assert "error" in result


def test_pick_problem_default_catalog_is_blind75():
    """No catalog arg -> the real, shipped blind75.json (backward compat)."""
    picked = server.pick_problem("junior")
    assert picked["difficulty"] == "easy"
    assert "url" in picked and "leetcode.com" in picked["url"]


def test_pick_problem_default_catalog_respects_exclude_ids():
    first = server.pick_problem("staff")
    second = server.pick_problem("staff", exclude_ids=[first["id"]])
    assert second["id"] != first["id"]


def test_pick_problem_data_modeling_catalog_covers_all_tiers():
    """The real, shipped data-modeling.json has a problem for every tier."""
    for tier in ["junior", "mid", "senior", "staff", "head"]:
        picked = server.pick_problem(tier, catalog="data-modeling")
        assert "error" not in picked, f"tier {tier}: {picked}"
        assert picked["difficulty"] == tier
        assert picked["domain"] in {"pnc_personal_lines", "health"}


def test_pick_problem_data_modeling_catalog_respects_exclude_ids():
    first = server.pick_problem("head", catalog="data-modeling")
    second = server.pick_problem("head", catalog="data-modeling", exclude_ids=[first["id"]])
    assert second["id"] != first["id"]


def test_pick_problem_rejects_catalog_path_traversal(widgets_catalog, tmp_path):
    secret = tmp_path / "secret.json"
    secret.write_text(json.dumps({"tier_difficulties": {}, "problems": []}))
    result = server.pick_problem("junior", catalog="../secret")
    assert "error" in result


def test_pick_problem_rejects_absolute_catalog_path(widgets_catalog, tmp_path):
    secret = tmp_path / "secret.json"
    secret.write_text(json.dumps({"tier_difficulties": {}, "problems": []}))
    result = server.pick_problem("junior", catalog=str(secret)[:-5])
    assert "error" in result


def test_pick_problem_malformed_catalog_json_returns_error(widgets_catalog):
    (widgets_catalog / "broken.json").write_text("{not valid json")
    result = server.pick_problem("junior", catalog="broken")
    assert "error" in result


def test_pick_problem_problem_missing_difficulty_key_is_skipped_not_crashed(widgets_catalog):
    (widgets_catalog / "sparse.json").write_text(
        json.dumps(
            {
                "tier_difficulties": {"junior": ["easy"]},
                "problems": [{"id": "no-difficulty"}, {"id": "w1", "difficulty": "easy"}],
            }
        )
    )
    result = server.pick_problem("junior", catalog="sparse")
    assert result["id"] == "w1"
