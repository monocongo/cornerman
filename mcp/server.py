#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "mcp[cli]>=1.2.0",
# ]
# ///
"""Cornerman MCP server.

State + timers + problem-catalog picker for the Cornerman interview coach
skill. SQLite-backed. Runs over stdio.

Tools:
  session_start        Create a session, return session_id.
  session_get          Load full session state (dossier + rounds + scores).
  session_update       Merge a value into the dossier at a dotted path.
  round_start          Record start of a take-home round; return start_iso
                       and auto_grade_at_iso (caller schedules the callback).
  round_end            Record end of a take-home round; return elapsed_minutes.
  score_save           Persist a 1-5 rubric score for a dimension.
  sessions_list        List past sessions for a candidate with their scores.
  pick_problem         Return a problem/scenario from a named catalog for a
                       seniority tier (default catalog: blind75).

Problem catalogs live under data/catalogs/*.json, one file per catalog
(e.g. blind75.json, data-modeling.json). Each is a JSON object with
`tier_difficulties` (tier -> list of difficulty tags valid for that tier
in this catalog) and `problems` (a list of dicts, each carrying at least
`id` and `difficulty`; other fields are catalog-specific and passed
through to the caller as-is).
"""

from __future__ import annotations

import json
import random
import sqlite3
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer

DB_PATH = Path.home() / ".cornerman" / "cornerman.db"
CATALOGS_DIR = Path(__file__).parent / "data" / "catalogs"
DEFAULT_CATALOG = "blind75"

mcp = MCPServer("cornerman")


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL,
            target_role TEXT,
            track TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            dossier TEXT NOT NULL DEFAULT '{}'
        );
        CREATE TABLE IF NOT EXISTS rounds (
            session_id TEXT NOT NULL,
            phase TEXT NOT NULL,
            problem TEXT,
            start_iso TEXT NOT NULL,
            end_iso TEXT,
            time_budget_minutes INTEGER,
            PRIMARY KEY (session_id, phase)
        );
        CREATE TABLE IF NOT EXISTS scores (
            session_id TEXT NOT NULL,
            dimension TEXT NOT NULL,
            score INTEGER NOT NULL,
            justification TEXT,
            saved_at TEXT NOT NULL,
            PRIMARY KEY (session_id, dimension)
        );
        """
    )
    _migrate(conn)
    return conn


def _migrate(conn: sqlite3.Connection) -> None:
    """Add columns introduced after a database may already exist on disk.

    CREATE TABLE IF NOT EXISTS is a no-op against an existing table, so a
    `~/.cornerman/cornerman.db` created before the `track` column existed
    would silently lack it. Guard with PRAGMA table_info and backfill.
    """
    cols = {row["name"] for row in conn.execute("PRAGMA table_info(sessions)")}
    if "track" not in cols:
        conn.execute("ALTER TABLE sessions ADD COLUMN track TEXT NOT NULL DEFAULT ''")


def _now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _set_nested(d: dict, dotted_path: str, value: Any) -> None:
    keys = dotted_path.split(".")
    for k in keys[:-1]:
        nxt = d.get(k)
        if not isinstance(nxt, dict):
            nxt = {}
            d[k] = nxt
        d = nxt
    d[keys[-1]] = value


def _coerce_value(value: str) -> Any:
    """Accept JSON strings for nested objects, fall back to raw string."""
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


@mcp.tool()
def session_start(candidate_id: str, target_role: str = "", track: str = "") -> dict:
    """Create a new interview session.

    Call once at intake. Store the returned session_id somewhere durable
    (in the dossier itself) and pass it to every subsequent tool call.

    `track` is the selected track id (e.g. "backend-ic", "data-ai-leadership")
    once it's known. It's fine to call session_start before the track is
    confirmed and pass "" — persist the real value into the dossier via
    session_update once it's decided; this column exists mainly so
    sessions_list and cross-session trend commentary can filter by track.
    """
    session_id = uuid.uuid4().hex[:12]
    now = _now_iso()
    with _connect() as db:
        db.execute(
            "INSERT INTO sessions (id, candidate_id, target_role, track, created_at) VALUES (?, ?, ?, ?, ?)",
            (session_id, candidate_id, target_role, track, now),
        )
    return {"session_id": session_id, "created_at": now}


@mcp.tool()
def session_get(session_id: str) -> dict:
    """Return the full session — dossier, rounds, scores.

    Used by the evaluator at end-of-interview and by any scheduled callback
    that needs to resume state after the conversation was closed.
    """
    with _connect() as db:
        row = db.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not row:
            return {"error": f"session {session_id} not found"}
        rounds = [dict(r) for r in db.execute("SELECT * FROM rounds WHERE session_id = ?", (session_id,)).fetchall()]
        scores = [dict(s) for s in db.execute("SELECT * FROM scores WHERE session_id = ?", (session_id,)).fetchall()]
    return {
        "session_id": row["id"],
        "candidate_id": row["candidate_id"],
        "target_role": row["target_role"],
        "track": row["track"],
        "created_at": row["created_at"],
        "dossier": json.loads(row["dossier"]),
        "rounds": rounds,
        "scores": scores,
    }


@mcp.tool()
def session_update(session_id: str, path: str, value: str) -> dict:
    """Merge a value into the dossier at a dotted path.

    Path is dotted, e.g. `hld.tradeoff_reasoning`. Value may be a JSON string
    (for nested objects/arrays) or a plain string.
    """
    with _connect() as db:
        row = db.execute("SELECT dossier FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not row:
            return {"error": f"session {session_id} not found"}
        dossier = json.loads(row["dossier"])
        _set_nested(dossier, path, _coerce_value(value))
        db.execute(
            "UPDATE sessions SET dossier = ? WHERE id = ?",
            (json.dumps(dossier), session_id),
        )
    return {"ok": True, "path": path}


@mcp.tool()
def round_start(session_id: str, phase: str, problem: str, time_budget_minutes: int) -> dict:
    """Record the start of a take-home round.

    Returns `start_iso` and `auto_grade_at_iso`. The caller (Cornerman's
    coding or HLD persona) should use `auto_grade_at_iso` as the `fireAt`
    for a `scheduled-tasks` MCP entry so grading fires even if the
    candidate doesn't return.
    """
    now = datetime.now(UTC)
    end_at = now + timedelta(minutes=time_budget_minutes)
    with _connect() as db:
        db.execute(
            """INSERT OR REPLACE INTO rounds
               (session_id, phase, problem, start_iso, end_iso, time_budget_minutes)
               VALUES (?, ?, ?, ?, NULL, ?)""",
            (session_id, phase, problem, now.isoformat(timespec="seconds"), time_budget_minutes),
        )
    return {
        "session_id": session_id,
        "phase": phase,
        "start_iso": now.isoformat(timespec="seconds"),
        "auto_grade_at_iso": end_at.isoformat(timespec="seconds"),
        "time_budget_minutes": time_budget_minutes,
    }


@mcp.tool()
def round_end(session_id: str, phase: str) -> dict:
    """Record the end of a take-home round. Returns elapsed_minutes.

    Call when the candidate submits (or immediately after grading, if the
    scheduled auto-grade fired).
    """
    now = datetime.now(UTC)
    with _connect() as db:
        row = db.execute(
            "SELECT start_iso, time_budget_minutes FROM rounds WHERE session_id = ? AND phase = ?",
            (session_id, phase),
        ).fetchone()
        if not row:
            return {"error": f"no round started for session {session_id} phase {phase}"}
        db.execute(
            "UPDATE rounds SET end_iso = ? WHERE session_id = ? AND phase = ?",
            (now.isoformat(timespec="seconds"), session_id, phase),
        )
    start = datetime.fromisoformat(row["start_iso"])
    elapsed_min = (now - start).total_seconds() / 60
    budget = row["time_budget_minutes"]
    return {
        "session_id": session_id,
        "phase": phase,
        "end_iso": now.isoformat(timespec="seconds"),
        "elapsed_minutes": round(elapsed_min, 2),
        "time_budget_minutes": budget,
        "overran": elapsed_min > budget if budget else False,
    }


@mcp.tool()
def score_save(session_id: str, dimension: str, score: int, justification: str) -> dict:
    """Persist a 1-5 rubric score for a dimension.

    Dimension is free text — it just needs to match a dimension `id` in the
    active track's `rubric` (see tracks/<track>/track.yaml). Reference:
    backend-ic: technical_depth, impact_ownership, coding, hld, lld,
    communication, jd_fit. data-ai-leadership: technical_depth,
    impact_ownership, data_modeling, platform_architecture, ai_ml_systems,
    governance_risk, insurance_domain_fluency, leadership_altitude,
    communication, jd_fit.
    """
    if not 1 <= score <= 5:
        return {"error": "score must be an integer between 1 and 5"}
    with _connect() as db:
        db.execute(
            """INSERT OR REPLACE INTO scores
               (session_id, dimension, score, justification, saved_at)
               VALUES (?, ?, ?, ?, ?)""",
            (session_id, dimension, score, justification, _now_iso()),
        )
    return {"ok": True, "session_id": session_id, "dimension": dimension, "score": score}


@mcp.tool()
def sessions_list(candidate_id: str) -> dict:
    """List past sessions for a candidate with per-dimension scores.

    Use to answer 'am I trending up?' — the evaluator can compare today's
    scorecard to prior sessions.
    """
    with _connect() as db:
        sessions = db.execute(
            "SELECT id, target_role, track, created_at FROM sessions WHERE candidate_id = ? ORDER BY created_at DESC",
            (candidate_id,),
        ).fetchall()
        out = []
        for s in sessions:
            scores = db.execute("SELECT dimension, score FROM scores WHERE session_id = ?", (s["id"],)).fetchall()
            out.append(
                {
                    "session_id": s["id"],
                    "target_role": s["target_role"],
                    "track": s["track"],
                    "created_at": s["created_at"],
                    "scores": {r["dimension"]: r["score"] for r in scores},
                }
            )
    return {"candidate_id": candidate_id, "sessions": out}


def _load_catalog(catalog: str) -> dict | None:
    path = CATALOGS_DIR / f"{catalog}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


@mcp.tool()
def pick_problem(tier: str, catalog: str = DEFAULT_CATALOG, exclude_ids: list[str] | None = None) -> dict:
    """Pick one problem/scenario from a catalog for the given seniority tier.

    tier: a tier name valid for the chosen catalog (e.g. 'junior' | 'mid' |
    'senior' | 'staff' for blind75; blind75 has no 'head' tier).
    catalog: catalog id, matching a file under data/catalogs/ (default
    'blind75'). Tracks with their own take-home rounds pass their own
    catalog id, e.g. 'data-modeling'.
    exclude_ids: problem `id`s the candidate has already seen in prior sessions.
    Returns the problem dict (fields vary by catalog; blind75 has id, name,
    category, difficulty, url) or an error.
    """
    exclude = set(exclude_ids or [])
    data = _load_catalog(catalog)
    if data is None:
        return {"error": f"catalog {catalog!r} not found under {CATALOGS_DIR}"}
    tier_difficulties = data.get("tier_difficulties", {})
    difficulties = tier_difficulties.get(tier)
    if difficulties is None:
        return {"error": f"unknown tier {tier!r} for catalog {catalog!r}; expected one of {sorted(tier_difficulties)}"}
    candidates = [p for p in data.get("problems", []) if p["difficulty"] in difficulties and p["id"] not in exclude]
    if not candidates:
        return {"error": f"no problems available for tier {tier!r} in catalog {catalog!r}"}
    return random.choice(candidates)


if __name__ == "__main__":
    mcp.run()
