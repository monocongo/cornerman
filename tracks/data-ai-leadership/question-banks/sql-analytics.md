# Question Bank — SQL & Analytics Engineering

**Seed topics, not a script.** Use during the data-modeling round's walkthrough when the
candidate's submission includes SQL/dbt code, or as a live follow-up drill on top of their design.
Same escalation ladder: conceptual → applied → edge/failure.

---

## Window functions

- Running/rolling aggregates: a trailing-12-month earned premium or claims-paid figure. Why
  `SUM(...) OVER (ORDER BY ... ROWS BETWEEN ...)` instead of a self-join or a subquery — what's
  the practical difference at scale?
- `ROW_NUMBER()` vs. `RANK()` vs. `DENSE_RANK()` — pick a scenario where the choice actually
  changes the result (e.g., picking "the latest policy version as of a date" when two versions
  share an effective date) and make them justify the pick.
- Partitioning correctness: for "the current version of each policy," what exactly is the
  `PARTITION BY` and `ORDER BY`, and what happens if a tie isn't broken deterministically?

## Point-in-time-correct joins

- Given a fact table and a Type 2 dimension, write (or describe) the join condition that returns
  the dimension row valid *as of the fact's own date* — not `is_current`. What are the boundary
  conditions on the `BETWEEN valid_from AND valid_to` (inclusive/exclusive) and why do they matter
  at the exact moment a new version becomes effective?
- What happens if the dimension has a gap (no version covers a given date) — does the join
  silently drop the fact (inner join) or surface a null (left join)? Which is correct for this
  scenario, and how would you catch the gap before it ships?

## Gaps and islands

- Given a table of eligibility spans (or policy-active periods) per member/policy, identify
  overlapping or contiguous spans and collapse them into a single span — the classic gaps-and-
  islands pattern. Can they describe an approach (window function comparing each row's start to
  the running max of prior end dates) without necessarily writing flawless SQL live?
- Applied version: "a member has three separate eligibility rows due to source-system re-syncs
  that are actually one continuous span — how would you detect and collapse that?"

## Deduplication on replayed data

- A source system (or a CDC/replication pipeline) resends the same record multiple times —
  exactly-once delivery isn't guaranteed. Given a natural key plus a source timestamp, how do you
  land the correct single row (`ROW_NUMBER() OVER (PARTITION BY natural_key ORDER BY source_ts
  DESC)`, or a merge/upsert)? What's different about deduplicating a *dimension* (want the latest
  state) vs. a *fact/ledger* table (want every transaction, deduplicated only against exact
  replays)?
- What breaks if the dedup key is wrong — too narrow (loses legitimate multiple records) or too
  wide (silently drops real transactions)?

## Incremental models

- Why incremental instead of full-refresh for a large fact table — what's the actual cost being
  avoided?
- What's the incremental predicate (`WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})`
  or similar) and what does it miss? Late-arriving records with an old `updated_at` but a new
  arrival time are the classic failure — does their incremental strategy handle that, or silently
  lose them?
- Backfill story: if the incremental logic changes, how do they reprocess history without a full
  rebuild becoming the only option?

## Loss triangles and cohort-style aggregation (P&C-flavored, transfers to any cohort report)

- Given a claim-transaction fact table at the right grain (one row per claim, per transaction,
  per booked date), describe the query that produces an accident-period × development-period
  triangle — a `GROUP BY` and a date-difference bucketing, nothing exotic, *if* the grain is
  right. If the candidate's model from the data-modeling half of this round can't support this
  query without a redesign, that's a real signal the grain was wrong.
- Same shape, health-flavored: a cohort retention or cost-development report by enrollment month
  — same underlying pattern (bucket by two time dimensions, aggregate).

## Anti-patterns to listen for

- Reaching for a self-join or a correlated subquery where a window function is the obviously
  better tool — not disqualifying alone, but ask "is there a way to do this without a self-join"
  and see if they get there.
- Deduplicating with `SELECT DISTINCT *` as a first instinct on a ledger/fact table — this hides
  the actual duplicate-detection logic and usually produces the wrong grain silently.
- No incremental predicate story at all ("we'd just full-refresh") on a fact table sized in the
  hundreds of millions of rows — fine as an initial answer, a gap if they can't reason about what
  breaks as it scales.
