# interview-coach

A Claude Skill that runs a realistic, adaptive technical mock interview against a specific job. Multi-phase, turn-by-turn, with an honest scorecard and study plan at the end.

## What it does

Given your resume and a job description, the skill:

1. Reads the resume, classifies your seniority (junior / mid / senior / staff), and builds an interview plan.
2. Runs a project deep-dive — probes for real impact first, drops into technical fundamentals when the impact story is thin.
3. Bridges your background to the target JD's actual requirements.
4. Switches into a staff-architect persona for a **system design (HLD)** problem sized to your level.
5. Zooms into the same system for **low-level design (LLD)** — data model, APIs, concurrency, edge cases.
6. Delivers a structured scorecard, honest hire signal, and study plan.

It's a sparring partner, not a cheerleader. Expect deliberate pressure and evidence-tied feedback.

## How to invoke

In a Claude conversation, provide:

- **Your resume** — upload a PDF/DOCX or paste the text.
- **The target role** — a JD text, a job posting URL, or a company URL + role title.
- **Say something like** "interview me for this role", "run a mock interview", or "prep me for this JD".

The skill will trigger and start with intake.

### Optional at intake

- **Session mode** — full run (default) or single-phase ("just do system design", "just LLD on my payments project").
- **Harshness dial** — `supportive coach`, `standard interviewer` (default), or `brutal bar-raiser`. Changes tone, not scores.

## What to expect

- **One question per turn.** The skill will ask, then wait. Answer as you would in a real interview.
- **Phase handoffs are announced.** You'll be told when the interview switches to system design vs. LLD vs. wrap-up.
- **No live grading.** The interviewer stays neutral in the moment. Feedback comes in the report at the end.
- **You can stop any time.** Say "stop" or "wrap it up" and you'll get a partial report scoped to what was covered.

## Structure

```
interview-coach/
├── SKILL.md                            # Orchestrator: intake → phase routing → report
├── references/
│   ├── 00-intake-analyst.md            # Parse resume + JD, classify seniority, build plan
│   ├── 01-experience-interviewer.md    # Project walk + impact probe + technical fallback
│   ├── 02-jd-alignment.md              # Bridge past experience to the target role
│   ├── 03-architect-hld.md             # System design persona (HLD)
│   ├── 04-architect-lld.md             # Low-level design persona
│   ├── 05-evaluator.md                 # Scoring rubric + final report generator
│   ├── seniority-calibration.md        # Difficulty matrix used by every persona
│   └── question-banks/
│       ├── backend.md
│       ├── ml-llm.md
│       └── system-design.md
├── assets/
│   └── report-template.md              # Fixed structure for the final feedback report
└── README.md
```

## Domain coverage

Question banks are seeded for **backend**, **ML/LLM**, and **general SWE / system design**. The interviewer follows your actual project domain — the banks are inspiration, not a script.

## Design notes

- **Persona-per-file.** There are no live sub-agents in claude.ai — each "interviewer" is a self-contained reference file the orchestrator loads at the start of its phase. Different phase, different voice.
- **Turn-by-turn is enforced.** The orchestrator's top rule is "ask one question, stop, wait". Every persona file reinforces it.
- **State lives in the conversation.** A shared `dossier` object accumulates through the phases; the evaluator reads the whole thing to write the final report. No disk persistence.
- **Auto-detected seniority, with confirmation.** The intake analyst reads your resume and shows you a calibration summary before the interview starts. Correct it if it's off — misclassification here poisons every later phase.
