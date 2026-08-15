# Insurance Reference Model

A dbt + DuckDB reference data model demonstrating bitemporal data-modeling patterns — SCD2
dimensions joined on effective date, append-only transaction ledgers, and PII/PHI boundary
enforcement — across two insurance domains: P&C personal auto and health claims. Built as both an
interview-drilling artifact and a portfolio piece.

## Running it

```bash
uv sync
uv run dbt build --profiles-dir .
```

Run from this directory. All data is synthetic seed data checked into `seeds/` — no external
dependencies, no credentials, no network access required. This also runs in CI on every push; see
`.github/workflows/dbt-build.yml` at the repo root.

## What this demonstrates

- **Grain declared on every fact/dim.** Every model's leading SQL comment states its grain
  explicitly, and `schema.yml` enforces the contract. See `docs/ADR-0001-grain-and-temporality.md`.
- **Loss/development triangles as a `GROUP BY` on an append-only ledger** — no bespoke snapshot
  process. See `analyses/pnc_loss_triangle.sql` and `analyses/health_development_triangle.sql`.
- **SCD2 dimensions joined on effective date, never on `is_current`.** A fact resolves the dimension
  row that was true as of its own date via a shared `as_of_join` macro. See
  `macros/as_of_join.sql`, used in `fct_claim.sql` and `fct_health_claim_line.sql`.
- **PII/PHI boundary enforced by a dbt test, not a comment.** See
  `tests/assert_fct_premium_earned_excludes_pii.sql` and
  `tests/assert_fct_adjudication_event_excludes_phi.sql`.

## Design decisions

- `docs/ADR-0001-grain-and-temporality.md` — grain, temporality, and why this uses regular models
  instead of dbt's native `snapshot` resource.
- `docs/ADR-0002-two-domains-not-conformed.md` — why P&C and health are two independent star
  schemas rather than a conformed dimension.
- `docs/ADR-0003-pii-phi-boundary.md` — how the PII/PHI boundary is enforced and what that
  enforcement does and doesn't cover.
- `docs/ERD.md` — entity-relationship diagrams for both domains.

## Scope note

This is intentionally small, synthetic, seeded data — not meant to be a large-scale benchmark.
Determinism and reviewability take priority over volume.
