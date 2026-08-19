# Question Bank — Data Platform Architecture

**Seed topics, not a script.** The persona builds one scenario from
`tracks/data-ai-leadership/calibration.md`'s per-tier "Problem class" table (see
`personas/platform-architecture.md` — there is no problem catalog for this phase), then
uses this bank to drive the walkthrough. Follow what they actually built; abandon the
list and chase what's interesting.

Escalation ladder is implicit for every topic, same as the backend track's HLD bank:
1. **Conceptual** — what is it, why does it exist?
2. **Applied** — why did you design it this way for *this* scenario?
3. **Edge / failure** — what breaks, or what's silently wrong, under Z?

---

## Junior tier

Single-source ingest to a queryable warehouse. The point is clean pipeline thinking, not
distributed-systems reasoning.

- What does "make it queryable same-day" actually require — batch schedule, load window,
  and how staleness is communicated to consumers?
- Where does schema validation happen — at load time, or does a bad row silently corrupt
  a downstream table?
- What's the retry story if the nightly extract job fails partway through?

**Constraint injections to have ready:**
- "What if the extract format changes without notice?"
- "What if the source sends the file twice?"

---

## Mid tier

Multi-source batch ingest with a transform layer and one named freshness SLA.

- How does the transform layer isolate a bad source from corrupting the whole run — does
  one malformed file block every other source's load?
- What's the actual mechanism behind the freshness SLA (e.g., "claims data must be
  same-day for the fraud team") — a scheduled job with a deadline, an SLA-monitoring
  alert, both?
- How do sources with different natural grains (daily extract vs. transactional feed) get
  reconciled into one transform layer without silently changing grain?

**Constraint injections to have ready:**
- "One source starts sending duplicate rows — what breaks downstream, and where do you
  catch it?"
- "The freshness SLA is missed two days in a row — how would you even know, and who
  finds out first?"

---

## Senior tier

Batch + streaming mix, a semantic layer serving multiple consumer teams, real
data-contract concerns between teams.

- What's the actual contract between a source team and the platform — a schema
  registry, a versioned API, a documented convention with no enforcement? What happens
  when it's violated?
- Why batch for some sources and streaming for others — is the split defended by a real
  latency requirement, or just "streaming is more modern"?
- Semantic layer: when two consumer teams define "active policy" slightly differently,
  where does that get resolved — in the semantic layer, or does each team query raw
  tables and diverge?

**Constraint injections to have ready:**
- "The claims team changes a field's meaning without telling you — how does your
  platform surface that before it corrupts a report?"
- "10× the source count."

---

## Staff tier

Multi-tenant or multi-line-of-business platform (auto + health on shared infrastructure),
lineage and cataloging as first-class, cost visibility per consumer.

- Multi-LOB isolation: is the boundary between lines of business (especially PHI-bearing
  health data and non-PHI auto data) a concrete mechanism — separate marts, row-level
  security, separate infrastructure — or a policy statement? Push for the mechanism, the
  same way `domain-packs/health.md` frames the PHI boundary problem.
- Lineage and cataloging: if a number in a report looks wrong, how does someone trace it
  back to the source column and transformation that produced it? Is this tooling, or
  institutional knowledge in one engineer's head?
- Cost visibility: what would it take to answer "what does the fraud team's usage cost us
  per month" — is cost attributable per consumer, or is it one shared bill?

**Constraint injections to have ready:**
- "Health data must never reach the auto team's warehouse — show the boundary."
- "Finance wants a cost-per-team breakdown — what does your platform need to support
  that?"

---

## Head tier

Same design surface as staff, plus an operating-model call: centralized platform team vs.
embedded analytics engineers vs. hub-and-spoke, and how that interacts with the
architecture.

- Operating model: who builds and owns the semantic layer — a central platform team, or
  each consumer team embedding their own analytics engineer against shared raw data? What
  does the candidate's architecture assume about who's accountable when a shared table
  breaks?
- Build vs. buy: for the cataloging/lineage/cost-visibility layer, is there a defended
  call on vendor vs. in-house, with a cost and lock-in tradeoff named explicitly?
- Vendor and regulatory exposure: does a proposed managed service introduce a data
  residency, vendor-lock-in, or audit concern that a Staff-level answer wouldn't need to
  consider?

**Constraint injections to have ready:**
- "The CFO cuts the platform budget 40% for next year — what do you cut, what do you
  keep, and what do you tell the CUO whose reports now run stale?"
- "You're acquiring a competitor with an incompatible policy admin system — walk me
  through the first two quarters of integration, not the end state."

---

## How to choose the problem

- Build the scenario from `calibration.md`'s "Problem class" column for the candidate's
  tier — do not invent a problem class outside that table.
- Continue whichever domain (P&C personal lines or health) the `data_modeling` round used;
  this round zooms out from the same subject area rather than switching domains.
- Answer clarifying questions with real insurance numbers from the active domain pack's
  "Representative scale" section — a mid-size P&C personal-lines carrier is roughly
  O(1–5M) active policies, O(100k–1M) claims/year, batch nightly extracts from policy
  admin as the default unless the candidate proposes CDC and defends why. Health lines
  add HIPAA/PHI boundary questions as a first-class constraint at every tier above
  junior.
- If in doubt, stick with the scenario built at the start of the phase. Do not switch
  mid-phase because the candidate is struggling — struggling is the signal.

## Anti-patterns

- Giving multiple scenarios in one phase.
- Reading requirements to the candidate. Let them ask.
- Prescribing components ("use a lakehouse here"). Let them propose.
- Grading whether they matched some canonical architecture. Grade the *reasoning* — why
  this component, what breaks, what it costs.
- Accepting a PHI/LOB boundary or a cost story as a policy statement rather than a
  concrete mechanism.
