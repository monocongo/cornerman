<p align="center">
  <img src="assets/logo.svg" alt="Cornerman logo" width="140" />
</p>

<h1 align="center">Cornerman 🥊</h1>

<p align="center">
  <em>A sparring partner, not a cheerleader.</em>
</p>

<p align="center">
  A Claude Skill that runs a realistic, adaptive technical mock interview against a specific job. Multi-phase, turn-by-turn, with an honest scorecard and study plan at the end.
</p>

---

## What it does

Give it your resume and a job description. It will:

1. Read the resume, classify your seniority (junior / mid / senior / staff), and build an interview plan.
2. Run a project deep-dive — probes for real impact first, drops into technical fundamentals when the impact story is thin.
3. Bridge your background to the target JD's actual requirements.
4. **Give you a coding problem (async take-home)** from the Blind 75, sized to your level. You solve it, paste your code, and Cornerman walks through your choices — correctness, complexity, brute-force vs. optimal.
5. Switch into a staff-architect persona for a **system design (HLD, async take-home)** — you sketch the design (whiteboard photo, Excalidraw, screenshot, whatever), upload it with a short written approach, and then walk through it in a live Q&A.
6. Zoom into the same system for **low-level design (LLD, live)** — data model, APIs, concurrency, edge cases.
7. Deliver a structured scorecard, honest hire signal, and study plan.

Expect deliberate pressure and evidence-tied feedback. That's the point — that's what a cornerman does between rounds.

### Async take-home phases

Two phases (coding and system design) run as take-home rather than live:

- **Setup** — Cornerman poses the problem and answers your clarifying questions with concrete numbers (e.g. "10M DAU, 100:1 read/write, p99 under 200ms"). Not "you decide" — real interviewer numbers.
- **Solve** — Cornerman records the start time to the MCP, schedules an auto-grade callback at your time budget (via the `scheduled-tasks` MCP), and waits silently. No hints.
- **Submit** — you paste code (coding) or upload a diagram + written explanation (system design). Cornerman cancels the auto-grade callback and grades the real submission.
- **Timeout branch** — if you never return, the scheduled callback fires in a fresh conversation, loads your session from disk, records the no-submit, and saves a floor score. You lose that round; the rest of the interview still stands.
- **Walkthrough** — after the grade, Cornerman runs a live Q&A on your specific choices.

## How to invoke

In a Claude conversation, provide:

- **Your resume** — upload a PDF/DOCX or paste the text.
- **The target role** — a JD text, a job posting URL, or a company URL + role title.
- **Say something like** "cornerman, interview me for this role", "run a mock interview", or "prep me for this JD".

Cornerman will trigger and start with intake.

### Optional at intake

- **Session mode** — full run (default) or single-phase ("just do system design", "just LLD on my payments project").
- **Harshness dial** — `supportive coach`, `standard interviewer` (default), or `brutal bar-raiser`. Changes tone, not scores.

## What to expect

- **One question per turn.** Cornerman asks, then waits. Answer as you would in a real interview.
- **Phase handoffs are announced.** You'll be told when the interview switches to system design vs. LLD vs. wrap-up.
- **No live grading.** The interviewer stays neutral in the moment. Feedback comes in the report at the end.
- **You can stop any time.** Say "stop" or "wrap it up" and you'll get a partial report scoped to what was covered.

## Structure

```
cornerman/
├── SKILL.md                            # Orchestrator: intake → phase routing → report
├── mcp/
│   ├── server.py                       # Cornerman MCP: sessions, timers, problem picker
│   └── data/
│       ├── blind75.json                # 71 Blind 75 problems (id, category, difficulty, url)
│       ├── blind75-source.md           # Original repo README (source of truth)
│       └── build_blind75.py            # Regenerates blind75.json from the source
├── references/
│   ├── 00-intake-analyst.md            # Session start, resume + JD, seniority classification
│   ├── 01-experience-interviewer.md    # Project walk + impact probe + technical fallback
│   ├── 02-jd-alignment.md              # Bridge past experience to the target role
│   ├── 03-architect-hld.md             # System design (HLD, async take-home)
│   ├── 04-architect-lld.md             # Low-level design (live)
│   ├── 05-evaluator.md                 # Scoring rubric + final report generator
│   ├── 06-coding-interviewer.md        # Coding (async take-home + walkthrough)
│   ├── seniority-calibration.md        # Difficulty matrix used by every persona
│   └── question-banks/
│       ├── backend.md
│       ├── coding-blind75.md
│       ├── ml-llm.md
│       └── system-design.md
├── assets/
│   ├── logo.svg
│   └── report-template.md              # Fixed structure for the final feedback report
└── README.md
```

## What each layer does

- **Skill (`SKILL.md` + `references/`)** — the interview logic. Works standalone as a skill; degrades gracefully if the MCP isn't installed.
- **MCP (`mcp/server.py`)** — persistent state. Sessions, per-round timers, rubric scores, past-session lookup, Blind 75 problem picker. SQLite at `~/.cornerman/cornerman.db`.

## Prerequisites

- A Claude environment that supports skills (claude.ai, Claude Code, or Cowork).
- **[`uv`](https://docs.astral.sh/uv/)** on your `PATH` — the MCP is a Python script that runs via `uv run`. Install with `brew install uv` on macOS or `curl -LsSf https://astral.sh/uv/install.sh | sh`.
- **Optional but recommended:** the `scheduled-tasks` MCP, for auto-grading async take-home rounds. Without it, timers still record but the timeout callback doesn't fire.

## Installation

Two steps. Install the skill folder, then register the MCP server.

**1. Install the skill:**

```bash
rm -rf ~/.claude/skills/cornerman
rsync -a --exclude='.git' --exclude='__pycache__' /path/to/cornerman/ ~/.claude/skills/cornerman/
```

**2. Register the MCP server** (Claude Code shown; adapt to your client):

```bash
claude mcp add cornerman --scope user -- uv run /path/to/cornerman/mcp/server.py
```

`--scope user` makes it available in every project. Drop it if you only want it in one project.

**3. (Optional)** install the `scheduled-tasks` MCP for auto-grading async take-home rounds. Without it, timers still record but the timeout callback doesn't fire — you just have to come back and paste your submission manually.

Restart your Claude client after installing. Verify with `claude mcp list` — you should see `cornerman` connected.

### Skill-only mode

If you don't have `uv` or don't want the MCP, step 1 alone works. You'll lose persistent state, past-session trend commentary, the automatic Blind 75 picker (falls back to `references/question-banks/coding-blind75.md`), and scheduled auto-grading. You keep: all the interview logic and the report.

### Rebuilding the Blind 75 catalog

The catalog is derived from [jaimin-bariya/blind-75-leetcode](https://github.com/jaimin-bariya/blind-75-leetcode). To refresh:

```bash
cd cornerman/mcp/data && python3 build_blind75.py
```

## Domain coverage

Question banks are seeded for **backend**, **ML/LLM**, **general SWE / system design**, and **coding (Blind 75, 71 problems, filtered by tier)**. Cornerman follows your actual project domain — the banks are inspiration for most rounds; the Blind 75 is used directly for coding (via `mcp__cornerman__pick_problem`).

## How it works under the hood

Three moving parts cooperate:

1. **The skill** loads persona files phase by phase. Each persona adopts a specific voice (analyst, interviewer, architect, evaluator), runs its round, then hands off.
2. **The `cornerman` MCP** persists everything to a SQLite file at `~/.cornerman/cornerman.db`: sessions, dossier state, per-round start/end timestamps, and rubric scores. It also serves the Blind 75 catalog for the coding round.
3. **The external `scheduled-tasks` MCP** (optional) is called for take-home timeouts. When you say "ready" on a coding or HLD round, Cornerman calls `round_start` (records `start_iso`, returns `auto_grade_at_iso`), then creates a scheduled task that fires at `auto_grade_at_iso` with a self-contained callback prompt. If you submit before the timer, Cornerman deletes the scheduled task. If you don't, the task fires in a new conversation, loads your session, and grades what's there.

Cornerman degrades gracefully at each layer: no `scheduled-tasks` → timers become best-effort in one conversation. No `cornerman` MCP → dossier lives in conversation memory only, no cross-session history.

## Design notes

- **Persona-per-file.** Each "interviewer" is a self-contained reference file the orchestrator loads at the start of its phase. Different phase, different voice.
- **Turn-by-turn is enforced.** The orchestrator's top rule is "ask one question, stop, wait". Every persona file reinforces it.
- **State is persistent when the MCP is installed.** Dossier, timers, and scores go to SQLite so scheduled callbacks can resume state and past sessions can be recalled for trend commentary.
- **Auto-detected seniority, with confirmation.** The intake analyst reads your resume and shows you a calibration summary before the interview starts. Correct it if it's off — misclassification here poisons every later phase.
- **Audio comes from the client.** Cornerman itself is text-in / text-out. If your client has voice mode (claude.ai voice, mobile), it works the same way through voice.

---

<p align="center">
  <sub>🥊 Get in the ring.</sub>
</p>
