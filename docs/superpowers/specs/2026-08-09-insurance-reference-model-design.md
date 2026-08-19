# Design — Insurance Reference Model (dbt + DuckDB)

**Date:** 2026-08-09
**Status:** Approved (pending final user sign-off on this document)
**Scope:** cornerman task 5 — `artifact/insurance-reference-model/`. Stays on the fork
(`monocongo/cornerman`); explicitly out of scope for any eventual upstream PR (see the plan file's
"Fork and upstream strategy").

## Context

`~/git/cornerman` is a fork of `TalalAhmed311/cornerman`, retargeted for Head of Data/AI interview
drilling with an insure-tech domain focus. Tasks 1–4 (track-selection spine, MCP generalization,
data-modeling interview round, domain packs) are done. This document designs task 5: a runnable
dbt + DuckDB reference data model, seeded with synthetic P&C personal-auto and health claims data,
that serves two purposes — a walkthrough artifact for the interview rounds, and a public portfolio
piece demonstrating data-platform judgment to a hiring panel.

Grounding material: `tracks/data-ai-leadership/domain-packs/pnc-personal-lines.md` and `.../health.md`
document the entities, bitemporal concepts, and representative scale this design is built from.
Four non-negotiable goals carried over from the original plan (`/Users/jadams/.claude/plans/merry-mapping-dove.md`):

1. Grain declared on every fact, in both the model docstring and `schema.yml`.
2. Loss triangles fall out of a `GROUP BY` — the demo query, not a bespoke pipeline.
3. SCD2 that matters: facts join dimensions on effective date, never on `is_current`.
4. A PII/PHI boundary enforced by a dbt test, not a comment.

## Decisions made in this design session

These extend (not replace) the decisions already locked in the plan file.

| # | Decision | Alternative considered | Why rejected |
|---|---|---|---|
| 1 | Health gets separate models for provider network-status (SCD2), authorization, and claim-line adjudication state | Denormalize onto `fct_health_claim_line` | Loses "as of service date" queryability that the health domain pack calls out as the actual point; would make health asymmetric in rigor vs. P&C |
| 2 | Synthetic data: small, hand-authored, static CSV seeds (~2 years of accident periods, low thousands of rows) | A scripted generator producing larger volumes / an explicit catastrophe-spike day | Static seeds are fast, free, deterministic, and easy to review; enough rows to make the triangle and SCD2 joins non-trivial without needing a generator to maintain |
| 3 | PII/PHI boundary enforced by tagging + a contract test on two specific facts; no masking macro | A `mask_phi`/tokenization macro for de-identified columns | No mart in this artifact needs PHI present-but-de-identified — only PHI-absent marts. A masking mechanism would be solving a problem this scope doesn't have |
| 4 | P&C and health are two independent stars, sharing only `dim_date` | A shared conformed `dim_party` across both lines | P&C and health don't naturally share customers in this data; forcing a conformed dimension would require a contrived entity-resolution narrative that isn't the point of the artifact |
| 5 | P&C gets an explicit party-role bridge (`fct_policy_party_role`) | Keep `dim_insured` simple, one row per primary named insured | Party-role multiplicity is named in the domain pack as the #1 place naive models double-count or lose history — cheap to model correctly, and specifically the kind of detail a panel would probe for |
| 6 | Health eligibility is its own span-grained fact (`fct_eligibility_span`), not an SCD2 attribute on `dim_member` | SCD2 rows on `dim_member` | SCD2 assumes one continuous state per key; eligibility has gaps (lapses) and needs to represent "no active coverage," which SCD2 doesn't naturally express |
| 7 | SCD2 dimensions use dbt's native `snapshot` feature | A hand-rolled `scd2_snapshot` macro | Standard, zero custom mechanism to maintain; the interview-relevant modeling knowledge is demonstrated in how snapshots are *joined*, not in reinventing SCD2 |
| 8 | CI runs `dbt build` only (seed + run + test) | Add `sqlfluff` linting | Keeps the pipeline focused on correctness, the actual point of the artifact, not tooling breadth |

## Directory shape

```
artifact/insurance-reference-model/
  seeds/
    pnc/            party.csv, policy.csv, policy_version.csv, coverage.csv,
                    claim.csv, claim_transaction.csv, policy_party_role.csv
    health/         member.csv, eligibility_span.csv, provider.csv,
                    provider_network_status.csv, benefit_plan.csv,
                    claim.csv, claim_line.csv, adjudication_event.csv,
                    authorization.csv
    date_spine.csv
  models/
    staging/
      pnc/          stg_pnc__party, stg_pnc__policy, stg_pnc__policy_version,
                    stg_pnc__coverage, stg_pnc__claim, stg_pnc__claim_transaction,
                    stg_pnc__policy_party_role
      health/       stg_health__member, stg_health__eligibility_span,
                    stg_health__provider, stg_health__provider_network_status,
                    stg_health__benefit_plan, stg_health__claim,
                    stg_health__claim_line, stg_health__adjudication_event,
                    stg_health__authorization
    marts/
      shared/       dim_date
      pnc/          dim_policy, dim_insured, dim_coverage, fct_claim,
                    fct_claim_transaction, fct_premium_earned,
                    fct_policy_party_role
      health/       dim_member, dim_provider, dim_benefit_plan,
                    fct_health_claim_line, fct_adjudication_event,
                    fct_eligibility_span, fct_authorization
    staging/pnc/schema.yml, staging/health/schema.yml
    marts/pnc/schema.yml, marts/health/schema.yml, marts/shared/schema.yml
  snapshots/         dim_policy.sql, dim_provider.sql, dim_benefit_plan.sql (native dbt snapshots)
  macros/            as_of_join.sql
  tests/             assert_fct_premium_earned_excludes_pii.sql
                     assert_fct_adjudication_event_excludes_phi.sql
  docs/
    ADR-0001-grain-and-temporality.md
    ADR-0002-two-domains-not-conformed.md
    ADR-0003-pii-phi-boundary.md
    ERD.md            (mermaid, one diagram per domain)
  dbt_project.yml, packages.yml, profiles.yml (DuckDB target, file-backed)
  .github/workflows/dbt-build.yml
```

Domain-scoped subfolders (`pnc/`, `health/`, `shared/`) under `staging/` and `marts/`, plus the
`stg_<domain>__<entity>` naming convention, make the "two independent stars" decision visible in
the file tree itself, not just in documentation.

## Models — grain and temporality

### P&C

- **`fct_claim`** — one row per claim **per header version** (`claim_id` + `valid_from`/`valid_to`
  in booked-date terms). `loss_date`/`report_date` fixed per claim; a new version is booked when
  header attributes change (status, assigned adjuster, classification).
- **`fct_claim_transaction`** — one row per claim, per coverage, per transaction, per
  `booked_date`. Append-only: `reserve_set`, `reserve_change`, `payment_issued`, `payment_voided`,
  `reopened`. Source of the loss-triangle demo query.
- **`fct_premium_earned`** — one row per policy, per coverage, per day of accrual. Joins
  `dim_policy`/`dim_coverage` on effective date. Finance-facing; carries no PII beyond policy/coverage
  keys (enforced by test — see below).
- **`fct_policy_party_role`** — one row per party, per policy or claim, per role
  (`named_insured`/`additional_insured`/`driver`/`claimant`/`beneficiary`), with effective dates.
- **`dim_policy`** — SCD2 snapshot, one row per policy per endorsement-effective period.
- **`dim_coverage`** — SCD2 snapshot, one row per policy version per coverage type.
- **`dim_insured`** — one row per party, current attributes only.

### Health

- **`fct_health_claim_line`** — one row per claim line **as submitted** (billed amount, service
  date, procedure/diagnosis codes). Does not store current adjudication state.
- **`fct_adjudication_event`** — one row per claim line, per status-transition event, per
  `booked_date`. Append-only: `received`, `pended`, `approved`, `denied`, `paid`, `adjusted`.
  Mirrors `fct_claim_transaction`; source of the health development-triangle demo query. Carries no
  diagnosis/procedure codes or member PHI beyond claim-line/member keys (enforced by test).
- **`fct_authorization`** — one row per authorization request, with its own `valid_from`/`valid_to`
  window, independent of eligibility and service date.
- **`fct_eligibility_span`** — one row per member per continuous coverage span (`start_date`,
  `end_date`, `plan_id`, `subscriber_id` if a dependent). Represents gaps and re-enrollment
  naturally; a member with no active span simply has no current-covering row.
- **`dim_provider`** — SCD2 snapshot, one row per provider per network-status-effective period.
- **`dim_benefit_plan`** — SCD2 snapshot, one row per plan per plan-year.
- **`dim_member`** — one row per member, current attributes only.

### Shared

- **`dim_date`** — the only model shared across both domains.

## Contracts and tests

- Every fact and dimension declares `config: {contract: {enforced: true}}` with explicit column
  types in `schema.yml`.
- Generic tests: `not_null`/`unique` on surrogate keys, `relationships` on foreign keys,
  `accepted_values` on enums (`transaction_type`, adjudication `event_type`, `network_status`).
- Sensitive columns are tagged in `schema.yml`: `meta: {pii: true}` (SSN, credit score on P&C
  party/insured models), `meta: {phi: true}` (diagnosis/procedure codes, demographic identifiers on
  `fct_health_claim_line`/`dim_member`).
- The PII/PHI boundary is enforced by two singular tests, not a comment:
  - `assert_fct_premium_earned_excludes_pii.sql` — queries `information_schema.columns` for the
    materialized `fct_premium_earned` table and fails if a forbidden PII column name is present.
  - `assert_fct_adjudication_event_excludes_phi.sql` — same mechanism, forbidden PHI column names,
    against `fct_adjudication_event`.
  - These two facts are the ones a finance/actuarial audience would plausibly consume and have no
    business reason to carry sensitive columns; the test catches a future accidental join that would
    leak one.

## Macros

One macro: `as_of_join` — joins a fact to an SCD2 snapshot dimension on effective-date range rather
than a natural key. No masking macro (decision 3) and no hand-rolled SCD2 macro (decision 7); SCD2
uses dbt's native `snapshot` feature for `dim_policy`, `dim_provider`, and `dim_benefit_plan`.

## Synthetic data

Hand-authored static CSV seeds under `seeds/pnc/` and `seeds/health/`. Target: enough rows to make
the loss-triangle and development-triangle demo queries visually meaningful (roughly 8–12 quarterly
accident/service periods, each with multiple development periods of transaction/event activity) and
enough policy/member volume to exercise SCD2 joins (mid-term endorsements, network-status changes,
benefit-plan renewals) without needing a data generator. No explicit catastrophe-spike scenario in
the seed data — that constraint is exercised narratively in the platform-architecture interview
round, not in this artifact's data.

## ADRs

- **ADR-0001 grain-and-temporality** — documents the append-only event-ledger pattern
  (`fct_claim_transaction`/`fct_adjudication_event`) as source of truth for current state, versioned
  header facts, and SCD2 dimensions joined on effective date. States the grain of every fact
  explicitly. Alternative considered: current-state-only columns; rejected because it can't
  reproduce a loss triangle or a prior reserve estimate.
- **ADR-0002 two-domains-not-conformed** — documents decision 4 (two independent stars, `dim_date`
  only shared). Alternative considered: conformed `dim_party`; rejected for lack of a natural
  entity-resolution story between an auto policyholder and a health plan member.
- **ADR-0003 pii-phi-boundary** — documents the tag-plus-contract-test mechanism (decision 3), and
  why a masking macro was scoped out.
- **ERD.md** — one mermaid diagram per domain (P&C, health), not a single merged diagram, matching
  the two-independent-stars decision.

## CI

`.github/workflows/dbt-build.yml`: on push/PR to the branch, `dbt seed && dbt build` against a
file-backed DuckDB target. No external services, no cost. Green build (models + tests) is the bar.
No linting step (decision 8).

## Demo queries

Two, one per domain, both falling out of a `GROUP BY` on an append-only ledger fact rather than a
bespoke pipeline:

- P&C loss triangle: `GROUP BY accident_period(loss_date), development_period(booked_date - loss_date)`
  on `fct_claim_transaction`.
- Health development triangle: `GROUP BY service_period(service_date), evaluation_period(booked_date - service_date)`
  on `fct_adjudication_event`, showing time-to-adjudicate development.

## Out of scope for this artifact

- Life & annuity and commercial/specialty/reinsurance domain packs (deferred at the plan level).
- A masking/tokenization macro (decision 3).
- A scripted synthetic-data generator or an explicit catastrophe-spike day in the seed data
  (decision 2).
- A conformed party dimension across P&C and health (decision 4).
- SQL linting in CI (decision 8).
- Upstream PR — this artifact and the domain packs stay on the fork per the plan's "Fork and
  upstream strategy."

## Next step

Once this document is approved, hand off to `superpowers:writing-plans` to produce the
implementation plan (model build order, seed authoring, per-model tests, CI workflow, ADR writeup),
then continue the existing fork-branch-commit-per-logical-unit workflow used for tasks 1–4.
