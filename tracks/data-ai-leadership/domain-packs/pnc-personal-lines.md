# Domain pack — P&C personal lines (auto & home)

Reference material for personas running scenarios in this line of business. Not read aloud to the
candidate — this is what the interviewer (you) needs to know to pose a realistic scenario, answer
clarifying questions with real numbers, and recognize a good answer when you hear one.

## The core entities

- **Party** — a person or organization. Can be a named insured, an additional insured, a driver
  who isn't a policyholder, a claimant, or a beneficiary. One party can play multiple roles across
  policies and claims — this is the #1 place naive models double-count or lose history.
- **Policy** — the contract. Has a `policy_number` (stable across the policy's life) and a
  **term** (e.g. 6 or 12 months). Renewals typically get a *new* policy period under the same
  `policy_number`, not a new number — a common grain mistake is treating `policy_number` as unique.
- **Policy version / endorsement** — mid-term changes (add a driver, change an address, add
  collision coverage, change a limit). Each endorsement has an `effective_date`. This is the
  textbook SCD Type 2 case: the policy dimension has a "state as of any date," not a single
  current state.
- **Coverage** — the specific promise (bodily injury liability, collision, comprehensive,
  dwelling, personal property...), each with limits and deductibles, attached to a policy version.
- **Vehicle / property (the "risk")** — what's actually insured. A vehicle can move between
  policies (sold, added to a new policy); a home is generally static but can be added/removed from
  a policy (e.g., a second home).
- **Claim** — filed against a policy period, tied to a **loss event** (an accident, a fire). One
  claim can touch multiple coverages (a single auto accident: collision damage + bodily injury +
  a rental car reimbursement — three coverages, one claim).
- **Claim transaction** — the append-only ledger under a claim: reserve set, reserve changed,
  payment issued, payment voided, claim reopened. **This is the fact table that matters most.**
  A claim's "current status" and "current reserve" are just the latest state of this ledger, never
  stored as the source of truth on the claim record itself.

## The three dates that aren't the same date (bitemporality, concretely)

This is the single highest-yield modeling concept in P&C claims, and the thing most candidates
who haven't worked in insurance get wrong on first pass:

- **Loss date** — when the accident/fire/theft actually happened.
- **Report date** — when the claim was reported to the carrier (can be days to years after loss —
  "IBNR", incurred but not reported, exists because of this gap).
- **Booked/transaction date** — when a given fact (a reserve estimate, a payment) was recorded in
  the system.

A reserve estimate made on 2026-03-01 for a loss that occurred 2026-01-15 and was reported
2026-01-20 has all three dates, and they're never collapsed into one. Reserves get **restated**
— a claim reopens, a new estimate is booked with a *new* booked date but the *same* loss date.
A good model can answer "what did we believe the reserve was, as of any past booked date" without
mutating history. A model that only stores "current reserve" cannot reproduce a prior quarter's
number — which actuarial and finance need to do routinely (reserve reviews, reinsurance
recoverable calculations, regulatory financial statements).

## Loss triangles — why claim-transaction grain matters

A **loss triangle** (accident-period × development-period) is the standard actuarial view of how
losses for a given accident period (e.g., "claims from accidents in Q1 2026") develop over
successive evaluation dates. If the claim-transaction fact is at the right grain (one row per
claim, per transaction, per booked/evaluation date), a triangle is a `GROUP BY accident_period,
development_period` away. If the model only stores current claim state, building a triangle
requires either a separate snapshot process or is simply impossible retroactively. This is a good
practical test of whether a candidate's data model actually supports the business, not just looks
clean on a whiteboard.

## Rating and telematics (if the candidate's scenario touches pricing)

- Rating factors (driver age, vehicle type, territory, prior claims, credit-based insurance score
  where legal, telematics-derived driving score) feed a rating engine at quote and renewal time.
  The **rating snapshot** at the time of quote/bind is itself something that may need to be
  preserved (to explain "why was this customer charged this premium" later, including to a
  regulator).
- Telematics (usage-based insurance) adds a high-volume, high-frequency source (trip-level or
  even second-level driving events) that has to be aggregated *before* it reaches the rating or
  claims-adjacent marts — a candidate proposing to join raw telematics events into the core claims
  star schema at claim grain is a modeling smell worth probing.

## Regulatory and fair-use context (surface only if the scenario/tier calls for it)

- Rate filings are state-regulated; carriers must be able to explain and reproduce how a rate was
  calculated for a given customer, sometimes years after the fact — another reason a rating
  snapshot / audit trail matters, independent of the AI-governance round's regulatory content.
  Colorado's SB21-169 (quantitative testing for unfair discrimination in algorithms/models used in
  insurance practices) is the most concrete example if a candidate needs one; don't require them to
  know the statute — see the `ai_governance` calibration overlay for the grading stance on that.

## Representative scale (use these numbers when a candidate asks for scope)

- Mid-size P&C personal-lines carrier: ~1–5M active policies, ~100k–1M claims/year, ~10–20
  active endorsement transactions per policy per year on average (most policies: zero; some:
  many).
- Nightly batch extract from the policy admin system is the default assumption unless the
  candidate proposes CDC (change data capture) and defends why (e.g., "the fraud team needs
  same-day visibility into new claims, batch doesn't meet that").
- Claim transaction volume is bursty around catastrophic events (a hailstorm, a hurricane) — a
  10–50× single-day spike in claim volume is a realistic constraint injection for this domain,
  parallel to "10× traffic" in a generic system-design round.
