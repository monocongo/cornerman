# ADR-0003: PII/PHI boundary enforced by a contract test

## Status
Accepted

## Context
Claims data carries PII (SSN, credit score) on the P&C side and PHI (diagnosis codes, procedure
codes, member demographics) on the health side. A finance/actuarial-facing mart (`fct_premium_earned`)
and an operational adjudication-tracking mart (`fct_adjudication_event`) have no business reason to
carry either — but a future contributor adding a column or an innocent-looking join could
accidentally leak one onto either fact, and a code comment saying "no PII here" would not catch
that at build time.

## Decision
Two mechanisms, layered:
1. **Tagging.** Every column that is PII or PHI is tagged `meta: {pii: true}` or `meta: {phi:
   true}` in `schema.yml` on the models where it legitimately lives (`dim_insured`, `dim_member`,
   `fct_health_claim_line`).
2. **A dbt singular test per protected mart**, not a comment. Each test
   (`assert_fct_premium_earned_excludes_pii.sql`, `assert_fct_adjudication_event_excludes_phi.sql`)
   uses `adapter.get_columns_in_relation` at compile/run time to check the actual materialized
   columns of its target model against a forbidden-column list, and fails the build (returns rows)
   if any forbidden column is present. This runs on every `dbt build`/`dbt test`, catching the leak
   the moment it's introduced rather than relying on someone remembering to check.

No masking or tokenization macro was built. Neither `fct_premium_earned` nor
`fct_adjudication_event` needs PII/PHI present-but-de-identified — they need it *absent*. A
masking mechanism would solve a problem this artifact doesn't have.

## Alternatives considered
- **A `mask_phi`/tokenization macro** applied to sensitive columns on marts that need a
  de-identified version of PII/PHI: rejected — no mart in this artifact has that requirement; every
  mart either legitimately carries the sensitive data (`dim_insured`, `dim_member`,
  `fct_health_claim_line`) or must not carry it at all (`fct_premium_earned`,
  `fct_adjudication_event`). Building a masking macro nobody calls would be scope inflation.
- **`information_schema.columns` query instead of `adapter.get_columns_in_relation`**: considered
  and rejected as the primary mechanism — it requires knowing the exact generated schema name
  (which depends on `generate_schema_name` and the `+schema:` config), which is fragile across
  environments. `adapter.get_columns_in_relation` resolves the relation the same way `ref()` does,
  so the test doesn't need to know the schema name at all.
- **A code comment / naming convention** ("don't join PII here"): rejected per the design doc's
  explicit goal — a comment doesn't fail a build.

## Consequences
- Adding a new sensitive column to `dim_insured` or `dim_member` requires only tagging it — the
  existing tests don't need to change, since the forbidden-column lists reference the *protected*
  marts' columns, not the source-of-truth dimensions.
- If a future column on `fct_premium_earned` or `fct_adjudication_event` needs to be added to the
  forbidden list, that's a one-line edit to the test file — the enforcement mechanism itself
  doesn't need to change.
