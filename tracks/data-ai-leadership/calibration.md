# Calibration overlay — data-ai-leadership

Read this alongside `references/seniority-calibration.md`, not instead of it. That file's tier
definitions and its tables for the **experience** and **JD alignment** phases apply here unchanged
— reuse them. This file adds the fifth tier this track needs, and supplies calibration tables for
the three phases this track swaps in: `data_modeling`, `platform_architecture`, `ai_governance`.

## The fifth tier: Head

`references/seniority-calibration.md` tops out at Staff/Architect — technical direction across
multiple systems. This track goes one rung further: someone accountable for a *function*, not just
its systems.

### Head (of Data / of AI)
- **Scope**: owns the data/AI org — headcount, budget, roadmap, vendor relationships, and how the
  function is measured by the rest of the company. Systems are a means, not the scope itself.
- **Design authority**: final on data/AI architecture decisions; also owns decisions a staff
  engineer would escalate — build vs. buy, platform consolidation vs. fragmentation, what gets
  funded this fiscal year and what gets cut.
- **Ambiguity handling**: expected to *generate* the requirements, not just receive ambiguous ones
  — including business requirements ("what should the data org even be responsible for at this
  company") and regulatory ones ("what does the AI Act's high-risk classification mean for our
  underwriting model, concretely, this quarter").
- **Concerns unique to this tier**: cost as a first-class design input (not an afterthought), talent
  and org structure (centralized vs. embedded vs. hub-and-spoke), vendor risk and lock-in, audit and
  regulatory exposure, how technical decisions read to a CFO/CUO/actuarial/legal audience who won't
  follow the architecture diagram.
- **What a Staff answer misses at Head**: a staff engineer can design the platform correctly and
  still miss the question a Head is actually being asked — "is this worth building, who owns it
  after you leave the room, and what does the board hear if it's wrong." Staff answers that stop at
  the technically-correct design, without a build-vs-buy call, a cost number, or a rollout/ownership
  story, are a gap at Head — not a gap at Staff.

## Leadership altitude — how it shows up without a separate round

This track does not run a standalone behavioral/exec round. Instead, every take-home and live phase
below injects at least one constraint that only makes sense to a candidate who has run a function,
not just a system: a budget cut, a regulator's request, an acquisition, a build-vs-buy fork, a
vendor renewal. The `leadership_altitude` rubric dimension is scored off how the candidate handles
*those* specific injections — not off general presence or confidence.

## Phase: data_modeling

| Tier | Scenario complexity | Time budget | What's expected |
|------|---------------------|-------------|------------------|
| Junior | Single entity family, one temporality concern (e.g., a policy dimension with SCD2). | 45 min | Correct grain, correct SCD2 mechanics. Bitemporal reasoning is a bonus, not expected. |
| Mid | Two related entity families with one cross-entity join concern (policy + claim). | 60 min | Grain declared explicitly; joins on effective date, not `is_current`; recognizes at least one temporality trap if prompted. |
| Senior | Full claims-or-policy subject area with bitemporal facts and a late-arriving/restated-data wrinkle. | 75 min | Grain declared unprompted; distinguishes transaction time from valid time unprompted; designs for late-arriving facts and reopened claims without being walked to it. |
| Staff | Same as senior, plus a cross-domain modeling choice (star vs. Data Vault vs. wide table) with an explicit tradeoff call. | 90 min | Defends the modeling paradigm choice against at least one alternative with a concrete reason ("Data Vault here because source systems will be added post-launch and we don't want to remodel the mart each time"), not a preference. |
| Head | Same design surface as staff, plus: what changes if this has to support both actuarial (needs point-in-time-correct history) and a regulator (needs an immutable audit trail) at once. | 90 min | Names the conflict between "cheap to query" and "provably immutable for audit" and picks a resolution with a cost/ownership story — e.g., "audit log is append-only and separately retained; the mart is a queryable projection of it, rebuildable, not the record of truth." |

**Constraint injections to have ready:** "Actuarial needs to reproduce last quarter's reserve number exactly, including which records were visible as of that date — does your model support that today?" · "A source system gets replaced next year — what has to change downstream?" · "Compliance asks: can you prove no record was silently edited? Point to the mechanism."

## Phase: platform_architecture

| Tier | Problem class | Time budget | Constraint injections expected |
|------|---------------|-------------|-------------------------------|
| Junior | Single-source ingest → warehouse → BI: e.g., "ingest daily policy extracts and make them queryable same-day." | 30 min | "What if the extract format changes without notice?" |
| Mid | Multi-source batch ingest with a transform layer and one freshness SLA (e.g., claims data must be same-day for the fraud team). | 45 min | "One source starts sending duplicate rows — what breaks downstream, and where do you catch it?" |
| Senior | Batch + streaming mix, a semantic layer serving multiple consumer teams, real data-contract concerns between teams. | 60 min | "The claims team changes a field's meaning without telling you — how does your platform surface that before it corrupts a report?" · "10× the source count." |
| Staff | Multi-tenant or multi-line-of-business platform (auto + health on shared infra), lineage and cataloging as first-class, cost visibility per consumer. | 75 min | "Health data must never reach the auto team's warehouse — show the boundary." · "Finance wants a cost-per-team breakdown — what does your platform need to support that?" |
| Head | Same surface as staff, plus an operating-model call: centralized platform team vs. embedded analytics engineers vs. hub-and-spoke, and how that interacts with the architecture. | 90 min | "The CFO cuts the platform budget 40% for next year — what do you cut, what do you keep, and what do you tell the CUO whose reports now run stale?" · "You're acquiring a competitor with an incompatible policy admin system — walk me through the first two quarters of integration, not the end state." |

**Notes for this phase specifically:** answer clarifying questions with real insurance numbers when the candidate asks for scale — a mid-size P&C personal-lines carrier is roughly O(1–5M) active policies, O(100k–1M) claims/year, batch nightly extracts from policy admin as the default unless the candidate proposes CDC and defends why. Health lines add HIPAA/PHI boundary questions as a first-class constraint at every tier above junior.

## Phase: ai_governance

Live round, not take-home. Same "one question, then stop" discipline as every other Cornerman phase.

| Tier | Depth expected |
|------|-----------------|
| Junior | Can describe train/serve skew and why it happens; knows evaluation needs a held-out set. |
| Mid | Has an actual eval set and metric for a shipped model; can describe one drift-detection approach; aware that "the model" and "the pipeline" fail differently. |
| Senior | Point-in-time-correct feature computation reasoned through explicitly (why joining features "as of" prediction time, not query time, matters); retraining trigger is a real policy, not "whenever"; rollback plan for a regressed model exists and is specific. |
| Staff | All of the above, plus: names the specific regulatory exposure of the model class they're discussing (e.g., a pricing or underwriting model is more exposed than an internal ops-efficiency model) and can sketch what a model-risk review of their own system would flag. |
| Head | Owns the governance *program*, not one model: has a point of view on centralized model-risk review vs. embedded team responsibility, can state what "high-risk" means under the EU AI Act Annex III for an insurance pricing/eligibility model in plain terms, and can describe how they'd respond if a regulator asked to see the fairness testing on a live model *today*, not hypothetically. |

**Constraint injections to have ready:** "This model sets a rate — walk me through what you'd need to show a regulator asking about disparate impact." (Senior+: expects familiarity with the shape of quantitative unfair-discrimination testing, e.g. the kind required under Colorado SB21-169, without expecting the candidate to cite the statute verbatim.) · "The model is used to deny or flag a claim — what's the adverse-action explanation story?" · "Health line: can this model see PHI it doesn't strictly need, and how would you know?" · "The model just regressed in production — walk me through the next hour."

**Grading note:** do not penalize a candidate for not knowing statute names or bulletin numbers. Penalize for not having *any* point of view on what a regulator or auditor would ask for. A Head candidate who says "I'd get legal and compliance in the room before we ship anything rate-affecting, and here's the specific evidence I'd want ready" is demonstrating the governance instinct even without citing SB21-169 by name. A candidate who has never considered that a pricing model might draw regulatory attention is the actual gap.

## The "level mismatch" case, restated for this track

Same principle as `references/seniority-calibration.md` — interview to the resume's level, score
against the target role's level, state both explicitly in the report. The place this bites hardest
in this track: a strong Staff-level technologist applying for a Head role who has never owned a
budget or a vendor relationship. That is not a technical gap and the report should say so plainly
— "technically staff-plus across the platform and modeling rounds; the delta to Head is operating
experience (budget, vendor, org design), not architecture skill" is a more useful sentence than a
single deflated score.
