# ADR-0002: Two independent domains, not a conformed dimension

## Status
Accepted

## Context
The artifact covers both P&C personal auto and health claims, matching the interview round's two
domain packs. A classic Kimball instinct is to build one conformed `dim_party` shared across every
line of business a "customer" touches.

## Decision
P&C and health are two independent star schemas. The only model shared between them is
`dim_date`. There is no conformed party/customer dimension linking a P&C policyholder to a health
plan member.

## Alternatives considered
- **A shared conformed `dim_party` across both lines**: rejected. This synthetic dataset has no
  natural overlap between P&C policyholders and health members — the two seed generators produce
  entirely separate party universes. Forcing a shared dimension would require inventing an
  entity-resolution narrative (probabilistic matching, a household concept, a data-quality
  process) that isn't what this artifact is meant to demonstrate. A real multi-line carrier does
  eventually need conformed customer dimensions, but building one on top of fabricated overlap
  would be modeling theater, not a real design decision.

## Consequences
- The file tree makes the boundary visible directly: `staging/pnc/`, `staging/health/`,
  `marts/pnc/`, `marts/health/`, plus a `marts/shared/` that holds only `dim_date`. Anyone browsing
  the repo sees the two-domains decision without reading this ADR first.
- If a third domain (life & annuity, commercial) were ever added to this artifact, the same
  question would need to be revisited with real justification, not retrofitted from this decision.
