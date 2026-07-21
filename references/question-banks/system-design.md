# Question Bank — System Design (HLD)

**These are HLD problem prompts, not a script.** The architect (Phase 3) picks **one** problem, sized to `dossier.candidate.seniority`, and drives the whole phase from that one problem. Do not switch problems mid-phase.

Every problem below is stated bare — no scaffolding. That's intentional. Watching whether the candidate asks for requirements is part of the assessment.

---

## Junior tier

These are single-service, single-datastore problems. The point is to see clean thinking, not distributed systems reasoning.

- Design a URL shortener.
- Design a notes app with sync across two devices for one user.
- Design a paste bin.
- Design a listings service for a small classifieds site (list, view, create, edit).
- Design a to-do app with reminders.

**Constraint injections to have ready:**
- "What if the table gets to 100M rows?"
- "What if 10× traffic?"
- "What if a user hits the create endpoint 100 times in a second by accident?"

---

## Mid tier

Systems that need a cache, a queue, or a background worker, and where a read/write asymmetry matters.

- Design a rate limiter (per-user, per-endpoint, single-region).
- Design a notification service (mobile push + email, best-effort delivery).
- Design an image upload + async processing pipeline (thumbnail, virus scan, CDN).
- Design an activity feed for a mid-size social app (fan-out on write vs. read).
- Design a simple job/scheduler service (submit jobs, retry on failure, dashboard).

**Constraint injections to have ready:**
- "Now 10× traffic — what's the first thing that breaks?"
- "The cache is inconsistent with the database for 30 seconds — is that OK for your product, and if not, what changes?"
- "One of your workers is stuck — how does the system notice, and what happens to the jobs it was holding?"

---

## Senior tier

Distributed designs where consistency, availability, and failure modes are real conversations.

- Design a distributed rate limiter across a global fleet.
- Design a chat system with delivery + read-receipt guarantees.
- Design a payments ledger with double-entry accounting and idempotent operations.
- Design a real-time collaborative document editor (single doc, many concurrent editors).
- Design a large-scale newsfeed with personalization and freshness constraints.
- Design a URL shortener at Twitter scale (yes the "junior" problem is a senior problem if you crank the constraints — this is fine if the seniority mismatch was flagged).

**Constraint injections to have ready:**
- "Now 100× traffic. What breaks first — and second?"
- "Now the write path has to be strongly consistent. What changes?"
- "The primary region just went down. Walk me through what happens to in-flight requests."
- "Two writers race for the same key. What's your guarantee?"

---

## Staff / architect tier

Multi-system, multi-region, or org-scale problems. The candidate is expected to drive requirements themselves and reason about cost, operational load, and migration.

- Design a global payments system with exactly-once processing across regions.
- Design an ad-serving system with strict tail-latency SLO and cost per impression as a first-class constraint.
- Design a data platform: ingest → storage → query → ML feature store, for a company with 100+ engineers using it.
- Design a migration: your monolith's user service needs to be extracted into its own service without downtime, over a quarter.
- Design a multi-tenant SaaS platform where tenants have wildly different scale (from 5 users to 500k users).
- Design a global feature-flag / config system with sub-second propagation and audit.

**Constraint injections to have ready:**
- "Now split-brain across two regions. What do you do?"
- "This has to be rolled out to production without downtime. Walk me through the rollout plan."
- "The finance team says your design costs 3× what they'll approve. What do you cut, and what do you keep?"
- "This system will be operated by an on-call rotation of engineers who didn't build it. What are they going to page you about?"

---

## How to choose the problem

- Look at `dossier.plan.hld_problem_candidate` — the intake analyst already picked one. Use it unless the candidate corrected their level at intake.
- Prefer a problem *adjacent* to the candidate's domain, not identical to their current job. If they've built payments, don't give them "design a payments system" — give them a design in an unfamiliar domain so you're testing thinking, not recall.
- If in doubt, pick one problem from the tier and stick with it. Do not switch mid-phase because they're struggling — struggling is the signal.

## Anti-patterns

- Giving multiple problems in one phase.
- Reading requirements to the candidate. Let them ask.
- Prescribing components ("use Kafka here"). Let them propose.
- Grading whether they matched some canonical answer. Grade the *reasoning*.
