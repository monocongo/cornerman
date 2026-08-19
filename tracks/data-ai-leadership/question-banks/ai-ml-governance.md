# Question Bank — AI/ML Systems & Governance

**Seed topics, not a script.** This phase is **live**, not a take-home — the persona
(`personas/ai-systems-governance.md`) anchors to the platform the candidate designed in
the prior round and uses this bank to drive the whole conversation. Follow what they
actually propose; abandon the list and chase what's interesting.

Escalation ladder is implicit for every topic, same as the other banks in this track:
1. **Conceptual** — what is it, why does it exist?
2. **Applied** — how would this actually work on the platform they just designed?
3. **Edge / failure** — what breaks, or what's silently wrong, under Z?

---

## Evaluation and held-out sets

- Is there an actual held-out evaluation set, or "we'll know it's working from user
  complaints"? What's the split strategy, and does it avoid leakage (e.g., the same
  policyholder's records appearing in both train and eval)?
- What metric, and does it match the business decision — a model that ranks well on AUC
  but is miscalibrated at the decision threshold the business actually uses is a real
  trap worth probing.
- How often is the eval set refreshed? A static eval set from launch stops measuring
  what matters as the population drifts.

## Train/serve skew

- Name a concrete way skew shows up on the platform they designed — a feature computed
  one way in a batch training pipeline and a different way in the online serving path
  (different null-handling, different aggregation window, a feature that simply isn't
  available at serve time).
- How would they detect skew before it causes a production incident, not just diagnose
  it after?

## Point-in-time-correct features

- For the platform from the prior round: are features computed "as of" prediction time,
  or "as of" query time? This is the same discipline the `data_modeling` question bank
  covers under "Point-in-time-correct joins" (`question-banks/sql-analytics.md`) —
  reference that section rather than re-deriving it; push the candidate to connect the
  two.
- What breaks if a feature pipeline silently joins on the wrong side of an SCD boundary
  and leaks future information into training data? How would they catch it before it
  ships, not after a model quietly overperforms in backtesting and underperforms live?

## Drift detection

- What's actually being monitored — input feature distributions, prediction
  distributions, or downstream outcome/label drift (which usually arrives late or never,
  depending on the label)?
- What does the monitor do when it fires — page someone, auto-disable the model, log and
  move on? A drift alert with no defined action is not a governance mechanism.

## Retraining policy

- Is there a retraining trigger, or is it "whenever we get around to it"? A real policy
  names a signal: a drift metric crossing a threshold, a scheduled cadence, a manual
  review gate before any retrained model ships.
- Who approves a retrained model going live, and what do they look at before approving?

## Rollback and incident response

- "The model just regressed in production — walk me through the next hour." Is there an
  actual rollback path (a previous model version kept warm, a feature flag, a fallback
  rule-based path) or does rollback mean an emergency deploy?
- What's persisted from the incident so it can be investigated afterward — logged
  predictions, the feature values at serve time, the model version?

## Regulatory exposure by model class

- What's the regulatory exposure of *this specific* model — a pricing or underwriting
  model is more exposed than an internal ops-efficiency model. Can the candidate name the
  difference unprompted, or do they treat all models as equally low-stakes?
- "This model sets a rate — walk me through what you'd need to show a regulator asking
  about disparate impact." Senior+: expects familiarity with the *shape* of quantitative
  unfair-discrimination testing (e.g., the kind required under Colorado SB21-169),
  without needing to cite the statute verbatim — see the grading note in
  `personas/ai-systems-governance.md`.
- "The model is used to deny or flag a claim — what's the adverse-action explanation
  story?" Is there a mechanism for producing a reason a denied claimant (or a regulator)
  could actually be given, or does the model's reasoning stop at a score?

## Model-risk review and governance program (staff+/head)

- Can the candidate sketch what a model-risk review of their own system would flag —
  concretely, not "it would probably pass"?
- Head tier: centralized model-risk review vs. embedded team responsibility — which, and
  why, for an organization at this scale? What does "high-risk" mean under the EU AI
  Act's Annex III for an insurance pricing/eligibility model, in plain terms?
- "How would you respond if a regulator asked to see the fairness testing on a live model
  *today*?" — tests whether governance is a real, ready artifact or a future intention.

## PHI minimization (health-line scenarios)

- Can this model see PHI it doesn't strictly need to make its prediction, and how would
  the candidate know? Same "concrete mechanism, not a policy statement" pressure as
  `domain-packs/health.md`'s PHI boundary question and
  `question-banks/data-platform.md`'s staff-tier isolation probe — push for a specific
  feature-selection or masking step, not "we'd minimize what we collect."

## Anti-patterns to listen for

- Treating governance as a separate "compliance" topic bolted onto the engineering,
  rather than the same discipline (a retraining policy *is* a governance mechanism, a
  rollback path *is* a risk control).
- "We'd have monitoring" with no named metric, threshold, or action on alert.
- Confident citation of statute names or acronyms with no underlying point of view on
  what they'd actually need to produce — this is name-dropping, not governance maturity,
  the same way a candidate name-dropping "Kafka" without a reason is a smell in the
  backend bank.
- No distinction between model classes by regulatory exposure — treating a pricing model
  and an internal dashboard model as equally low-stakes.
- Silence on rollback. If a candidate never raises "what if this regresses" unprompted at
  senior tier and above, that's the first thing to probe.
