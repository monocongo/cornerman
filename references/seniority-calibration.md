# Seniority Calibration Matrix

Every persona consults this before pitching a question or scoring an answer. The point is that "wrong" at senior is different from "wrong" at junior — the *ceiling* moves and so does what counts as a gap.

## The four tiers (scope, not years)

Years are a weak signal. Someone can be senior at 3 years or mid at 10. Read scope.

### Junior
- **Scope**: executes well-defined tickets; owns features under supervision; still building fundamentals.
- **Design authority**: none to local; asks before making non-trivial calls.
- **Ambiguity handling**: expects the problem to be scoped for them.
- **Mentorship**: receiving, not giving.

### Mid
- **Scope**: owns features end-to-end; picks local tech with justification; contributes to system-level discussions.
- **Design authority**: local — designs within a system others own.
- **Ambiguity handling**: can turn a vague ticket into a plan with one clarifying pass.
- **Mentorship**: onboards juniors; not yet setting technical direction.

### Senior
- **Scope**: owns systems, not just features; makes and defends tradeoff calls; drives design across a service.
- **Design authority**: system-level; expected to say no to bad ideas with justification.
- **Ambiguity handling**: comfortable turning "we need X somehow" into a design proposal.
- **Mentorship**: raises the level of the engineers around them; sets patterns.

### Staff / Architect
- **Scope**: multiple systems; sets technical direction; org-facing.
- **Design authority**: cross-team; owns architectural coherence; navigates competing stakeholders.
- **Ambiguity handling**: expected to drive requirements themselves, including business ones.
- **Concerns**: operational load, cost, migration risk, org fit of a technical choice.

## What each phase does at each tier

### Experience phase (`01-experience-interviewer.md`)

| Tier | Escalation ladder ceiling | Weight of "never shipped" |
|------|---------------------------|---------------------------|
| Junior | Rung 2 (applied). Rung 3 is a bonus. | Small — most juniors have limited shipping history. |
| Mid | Rung 3 (edge/failure) on at least one topic per project. | Medium — should have at least one real ship. |
| Senior | Rung 3 comfortably; expected to bring up edge cases unprompted. | Large — a senior with no shipping story is a real concern. |
| Staff | Rung 3 plus operational reasoning (cost, migration, blast radius). | Very large — staff without production impact is a red flag. |

### JD alignment (`02-jd-alignment.md`)

| Tier | Gap tolerance |
|------|---------------|
| Junior | Gaps on advanced role stack are normal; probe ramp story only. |
| Mid | Foundational gaps in the role's core stack matter; adjacent-tech gaps are fine with a ramp story. |
| Senior | Core stack should be present; missing an "advertised" senior-level tech is a real gap. |
| Staff | Should map history to nearly every top requirement; gaps here are notable. |

### Coding (`06-coding-interviewer.md`)

| Tier | Problem class | Time budget | Optimality expectation |
|------|---------------|-------------|-----------------------|
| Junior | Blind 75 Easy (Two Sum, Valid Parens, Reverse Linked List, Max Depth of Tree, etc.). | 45 min | Correct is the bar. Brute-force accepted if candidate can articulate the optimal on the walkthrough. |
| Mid | Blind 75 Medium (Merge Intervals, Coin Change, Number of Islands, LIS, Top K Frequent, etc.). | 45 min | Optimal expected first try. If brute-force, candidate must recognize it and describe the O-improvement. |
| Senior | Blind 75 Medium-Hard (Merge K Sorted Lists, Serialize/Deserialize Tree, Min Window Substring, Word Search II, etc.). | 60 min | Optimal expected. Interviewer probes complexity + edge handling. Space-optimality is fair game. |
| Staff | Usually skipped. If run: one Hard with systems-flavored discussion, or a data-structure design (LRU, Median from Data Stream, Alien Dictionary). | 60 min | Grading weight shifts to tradeoff articulation — memory/latency/throughput reasoning matters more than raw correctness. |

### HLD (`03-architect-hld.md`)

| Tier | Problem class | Constraint injections expected |
|------|---------------|-------------------------------|
| Junior | Single-service systems: URL shortener, basic feed reader, notes app with sync, a CRUD-scale marketplace listing service. | "What if the table gets big?" "What if 10× traffic?" |
| Mid | Systems with a cache/queue/DB and a real read-write asymmetry: rate limiter, notification service, activity feed for a mid-size app, image upload+processing pipeline. | 10× traffic, one cache-invalidation question, one basic failure. |
| Senior | Distributed designs with real consistency/availability decisions: newsfeed at scale, chat with delivery guarantees, a payments ledger, a distributed rate limiter. | 100× traffic, consistency-model change, primary-region loss. |
| Staff | Multi-system / multi-region / cross-org: global feed with regional locality, exactly-once payment across services, ad-serving with cost/latency constraints, migration of a critical live system. | Multi-region partition, cost/latency tradeoff, operational rollout, org-scale change. |

### LLD (`04-architect-lld.md`)

| Tier | Depth expected |
|------|----------------|
| Junior | Clean class model, correct basic REST API, one obvious index. Concurrency probe = optimistic "two clicks Submit". |
| Mid | Justified schema, idempotent API, one concurrency issue reasoned through with a specific mechanism (lock, CAS, transaction). |
| Senior | Failure modes designed into the API contract; specific isolation levels named; retry/backoff semantics articulated; observability discussed. |
| Staff | Consistency guarantees precisely stated; operational rollout thought through; cost/perf tradeoffs at data layer; failure blast radius mapped. |

### Scoring weight (`05-evaluator.md`)

The same evidence produces different scores at different tiers.

- "Named the tech but couldn't justify it" — a 3 for junior, a 2 for mid, a 1 for senior.
- "Reasoned about exactly-once semantics" — a 4 for senior, a 5 for mid, "beyond ceiling / positive signal" for junior.
- "Missed a multi-region consistency issue" — not a gap for junior/mid, a real gap for senior/staff.
- "Brute-force O(n²) solution on Two Sum, didn't mention the hashmap approach" — 3 for junior, 2 for mid, 1 for senior.
- "Optimal solution first try but couldn't articulate space complexity" — 4 for junior, 3 for mid/senior.

## The "level mismatch" case

Sometimes the resume reads mid but they're applying for senior (or vice versa). The intake analyst flagged this. Handling:

- Interview to the **resume's** level (that's where they actually are).
- Score against the **target role's** level (that's the bar they're being read against).
- The report should say both: "interviewed as a mid; scored against senior bar; delta is X".

Do not silently score against a bar the candidate isn't aware of. The report makes this explicit.
