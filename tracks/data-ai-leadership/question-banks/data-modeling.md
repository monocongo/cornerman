# Question Bank — Data Modeling

**Seed topics, not a script.** The persona picks one scenario from `mcp/data/catalogs/data-modeling.json`
(via `mcp__cornerman__pick_problem`), reads the candidate's submitted ERD/DDL/dbt sketch and
written temporality notes, then uses this bank to drive the walkthrough. Follow what they actually
built; abandon the list and chase what's interesting.

Escalation ladder is implicit for every topic, same as the backend bank:
1. **Conceptual** — what is it, why does it exist?
2. **Applied** — why did you model it this way in *this* scenario?
3. **Edge / failure** — what breaks, or what's silently wrong, under Z?

---

## Grain

- What is the grain of this fact table — state it in one sentence ("one row per X per Y")?
- Is the grain actually enforced (a uniqueness test on the grain-defining columns), or just
  intended?
- What happens if a source system starts sending two rows for what should be one grain instance
  (a duplicate, or a legitimate correction that looks like a duplicate)?
- Mixed-grain smell: does any single table quietly hold both header-level and line-level facts
  (the claim-header-vs-claim-line trap)? How would that show up as a bug downstream (double
  counting on a `SUM`, for instance)?

## Slowly changing dimensions (SCD)

- Why Type 2 here specifically — what would Type 1 (overwrite) silently lose?
- Walk through the exact columns: `effective_date` / `end_date` (or `valid_from` / `valid_to`),
  `is_current`. What determines when a new version row is created vs. when an existing row is
  updated in place?
- **The `is_current` trap**: a fact table joining a dimension on `is_current = true` instead of on
  the fact's own date, matched against the dimension's effective window. Ask directly: "if I ran
  this query today vs. run it again in six months against the same historical fact rows, would I
  get the same answer?" — if not, the join is wrong.
- What happens when two changes land on the same effective date (a same-day correction)? Is there
  a defined tie-break, or does the model silently pick one?

## Bitemporality

- Distinguish, explicitly: the date something was *true in the world* (valid time / effective
  time — a loss date, a service date) from the date it was *recorded in the system* (transaction
  time / booked time). Can the candidate name both for their scenario without being walked to it?
- Late-arriving facts: a fact whose valid-time is in the past but whose transaction-time is now
  (a claim reported months after the loss, a corrected diagnosis code submitted after the original
  claim). Does the model handle insertion without needing to rewrite already-published history?
- Restatement: something previously recorded turns out to be wrong and gets corrected (a reserve
  re-estimate, a claim reopened). Is the correction a *new* row with a new transaction-time, or a
  destructive update? Push for "how would you reproduce last quarter's number after this
  correction lands" — that's the real test.
- "As of" queries: can the candidate's model answer "what did we believe as of transaction-time T"
  and separately "what was true as of valid-time T" — these are two different questions and a
  naive model can only answer one, or neither.

## Modeling paradigm (star schema / Data Vault / One Big Table)

- Why this paradigm for this scenario — not "it's what I know," a reason tied to the scenario's
  actual pressures (source system churn, audit requirements, team size, query patterns).
- Star schema candidates: are dimensions properly conformed (shared across fact tables) or is
  there a dimension explosion / redundant modeling of the same entity?
- Data Vault candidates: can they explain what a hub, link, and satellite actually are, in their
  own words, applied to this scenario's entities — not just the vocabulary?
- OBT (one big table) candidates: what's the actual cost being accepted (reprocessing cost on
  late-arriving changes, storage, query complexity for consumers who need a different grain) —
  do they know the tradeoff or did they pick it because it's simple to start?
- Push on migration: "a year from now you need to add a second source system feeding this same
  subject area — what changes, and what stays the same?"

## Conformed dimensions and shared entities

- Does `party`/`insured`/`member` get modeled once and reused, or does each fact table roll its
  own copy of person attributes? What breaks when the same person needs to be recognized across
  two fact tables (a driver who is also a claimant, a subscriber who is also a dependent on
  another policy)?
- Surrogate keys vs. natural keys — which did they use for the dimension's primary key, and why?
  What happens if the natural key (a policy number, a member ID) gets reused or reassigned by the
  source system years later?

## PII / PHI segregation

- Which specific columns in this scenario are sensitive (diagnosis codes, SSNs, driver's license
  numbers)? Name them, don't wave at "the sensitive stuff."
- Where, mechanically, does segregation happen — a separate schema, a view that excludes the
  columns, a tokenization step before the data reaches a broad-access mart? "We'd be careful" is
  not an answer; push for the actual boundary.
- Who can join back from a de-identified/tokenized record to the real identity, and through what
  mechanism? If the answer is "anyone with warehouse access," that's a gap worth naming.

## Late-arriving and reopened entities (domain-specific edge cases)

- P&C: a claim closes, then reopens eight months later with a new reserve estimate. Walk through
  exactly what rows get written and what a query against the claim as of *last month* would
  return, both before and after the reopen.
- Health: a claim line denies, then gets appealed and approved on resubmission. Is the appeal a
  new claim, a new line, or a state transition on the existing line — and does the model preserve
  the fact that it was originally denied?

## Anti-patterns to listen for

- Modeling the "current state" table first and treating history as an afterthought ("we'll add
  SCD later") — history is usually the actual business requirement, not a nice-to-have.
- Reaching for Data Vault or a heavily normalized model reflexively, without a stated reason tied
  to this scenario's pressures — name-dropping a paradigm the same way a candidate name-drops a
  technology in the backend bank.
- Treating `is_current = true` as equivalent to "the correct row for a historical join." It never
  is.
- Silence on grain. If a candidate never states the grain of their fact tables unprompted at
  senior tier and above, that's the first thing to probe.
