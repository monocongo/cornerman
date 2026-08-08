# Domain pack — Health (payer side: claims, eligibility, risk adjustment)

Reference material for personas running scenarios in this line of business. Assumes a **payer**
context (health plan / insurer), not a provider EHR — that's a different domain with different
grain problems. Not read aloud to the candidate.

## The core entities

- **Member** — a covered person. Has **eligibility spans**: date ranges during which they were
  actively covered under a given plan. A member is not "active" or "inactive" as a single flag —
  they have a history of spans, and can have *gaps* (lapsed coverage, then re-enrolled) and
  *overlaps* across plan changes mid-year that a naive model collapses incorrectly.
- **Subscriber vs. dependent** — a member enrolls a subscriber (often an employee) plus
  dependents (spouse, children) under one **group** or **policy**. Claims and eligibility both
  need to resolve back to the right member, not just the subscriber.
- **Provider** — an individual clinician or a facility. Providers have **network status** that
  changes over time (in-network, out-of-network, terminated) — like the policy endorsement
  problem, this is temporal and affects how a claim from six months ago should be adjudicated
  *as of the network status on the date of service*, not today's status.
- **Claim / encounter** — a bill for services rendered. A single claim typically has multiple
  **claim lines** (one per service/procedure code), each independently priced, adjudicated, and
  potentially denied — the claim header and claim line are two different grains, and conflating
  them (storing "claim status" as if a whole claim is uniformly approved/denied) loses real
  information when some lines pay and others deny.
- **Authorization** — a pre-approval for a service, often required before a claim for that
  service will be paid. Authorizations have their own validity window, separate from the
  eligibility span and separate from the claim's service date.
- **Risk adjustment data** — diagnosis codes (ICD-10) roll up to **HCCs** (Hierarchical
  Condition Categories) under CMS's risk-adjustment model, used to adjust payments to plans based
  on member health risk. This is a real, high-stakes downstream consumer of claims data with its
  own correctness bar (submissions to CMS, audited).

## The temporality trap specific to this domain: "as of service date," not "as of today"

Adjudicating (or re-adjudicating, or auditing) a claim from the past has to be done **as of the
facts that were true on the date of service** — the member's eligibility as of that date, the
provider's network status as of that date, the benefit plan design as of that date (benefit
designs change at renewal, typically annually). A model that only stores "current member status,"
"current provider network status," and "current benefit design" cannot correctly re-price or
audit a historical claim — the same bitemporal discipline as the P&C claims pack, applied to
eligibility/network/benefit-design dimensions instead of policy/reserve.

**Adjudication itself is also stateful, not a single status.** A claim line moves through
states — received, in review, pended (missing info), approved, denied, paid, and can be
*adjusted* after initial payment (a correction, a clawback). Modeling "claim status" as a single
mutable field loses the ability to answer "how long did this line sit pended, and why" — an
operational question payers actually get asked (regulators, providers disputing denials).

## PHI and the boundary problem

Claims, diagnosis codes, and authorization data are Protected Health Information under HIPAA.
A recurring, concrete design question for this domain: **which columns are PHI, and where in the
pipeline do they get isolated or de-identified** — e.g., a cost-analytics mart used by a finance
team that doesn't need individual diagnosis codes should not receive raw ICD-10 columns just
because they were present in the source claim. A candidate who treats "PHI segregation" as a
policy statement rather than a concrete pipeline boundary (a specific mart, a specific
masking/tokenization step, a specific access-control layer) hasn't actually solved it — push for
the mechanism, the same way the P&C pack pushes for a concrete audit-trail mechanism, not just
"we'd be careful."

## Representative scale (use these numbers when a candidate asks for scope)

- Mid-size regional health plan: ~500k–2M covered members, ~5–15M claim lines/year (a single
  encounter can generate several lines), annual open-enrollment causing eligibility churn spikes.
- Claims typically arrive via batch EDI (X12 837 transactions) from clearinghouses, not
  real-time streams — batch nightly/intra-day is the default assumption unless the candidate
  proposes something else and defends it.
- Risk-adjustment submission cycles are periodic (aligned to CMS deadlines), not continuous —
  relevant if a candidate proposes a real-time pipeline for HCC data where a batch cycle would
  actually be the correct, defensible design (a good "don't over-engineer" signal to listen for).
