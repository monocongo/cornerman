# ADR-0001: Grain and temporality

## Status
Accepted

## Context
This artifact must let someone reproduce a prior reserve estimate, build a loss/development
triangle retroactively, and re-price a historical claim/claim-line "as of the facts true on the
date of service" — not as of today. That requires three distinct temporal mechanisms, applied
consistently across both domains: an append-only event ledger for anything that changes state
after the fact, versioned dimensions for anything with a mid-term change history, and explicit
as-of-date joins between the two.

## Decision
1. **Append-only ledgers are the source of truth for current state.** `fct_claim_transaction`
   (P&C) and `fct_adjudication_event` (health) never overwrite a row; a claim's current
   reserve/status is the latest row in the ledger, not a separately stored field. This is what
   makes a loss/development triangle a `GROUP BY accident_period, development_period` instead of a
   bespoke snapshot process.
2. **SCD2 dimensions (`dim_policy`, `dim_coverage`, `dim_provider`, `dim_benefit_plan`) are regular
   dbt models reading pre-versioned staging data, not dbt's native `snapshot` resource.** dbt
   snapshots build history by diffing a *mutable* source table across *multiple pipeline
   invocations over time* — the mechanism assumes you don't already know the history, you're
   accumulating it run by run. This artifact is the opposite case: ~2 years of endorsement/
   network-status/plan-year history is already known and must build clean in one `dbt build`
   inside CI. Running `dbt snapshot` once against static seed data would capture exactly one row
   per key — the history the artifact needs to demonstrate would never materialize. Instead, the
   staging layer is already version-grained (one row per endorsement, one row per network-status
   change, one row per plan-year), and `dim_policy`/`dim_coverage`/`dim_provider`/
   `dim_benefit_plan` simply select from it with `valid_from`/`valid_to`/`is_current` columns. The
   SCD2 *shape* (a queryable "as of any date" dimension) is preserved; only the *mechanism* that
   produces it differs from the original design's plan to use dbt `snapshot`.
3. **Facts join SCD2 dimensions on effective date via a shared `as_of_join` macro, never on
   `is_current`.** `fct_claim` resolves `policy_version_id_at_loss` from `dim_policy` as of
   `loss_date`; `fct_health_claim_line` resolves provider network status and benefit plan as of
   `service_date`. Neither fact stores a direct FK to "the current version" — a query against
   either fact always reflects the state that was true at the relevant historical date, matching
   the P&C and health domain packs' shared bitemporal requirement.
4. **Header facts stay simple where a ledger already captures the lifecycle.** `fct_claim` is one
   row per claim, not one row per header version — claim-level status transitions (including
   reopen) are `transaction_type` values in `fct_claim_transaction`'s ledger rather than a second,
   overlapping versioning mechanism for what is the same underlying event stream.

## Alternatives considered
- **Current-state-only columns** (a `current_status`/`current_reserve` field on the claim record
  itself): rejected — cannot reproduce a loss triangle or a prior reserve estimate, which is the
  artifact's core requirement.
- **dbt's native `snapshot` resource, run as originally specified**: rejected for the reason in
  decision 2 above — it doesn't fit a single-build, pre-known-history artifact.
- **A separate versioned header fact for `fct_claim`** (per the original design doc's grain of
  "one row per claim per header version"): rejected — status transitions are already an event
  stream in `fct_claim_transaction`; a second versioning mechanism for the same lifecycle would be
  redundant without adding queryable value.

## Consequences
- The artifact demonstrates the *querying* pattern (as-of joins, ledger-driven triangles) that a
  hiring panel actually cares about, without depending on a snapshot mechanism that doesn't
  technically work for pre-loaded synthetic history.
- A reader who only knows dbt's `snapshot` feature from tutorials may expect to find it in
  `snapshots/` and not find it there — this ADR is the answer to "where's the snapshot config?"
