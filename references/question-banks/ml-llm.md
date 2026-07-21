# Question Bank — ML / LLM

**Seed topics, not a script.** The interviewer follows the candidate's answers. Use when the resume or project maps to ML/LLM work.

Ladder is implicit for every topic:
1. **Conceptual** — what is it?
2. **Applied** — why did you choose it in your project?
3. **Edge / failure** — what breaks under Z?

---

## Data pipeline

- Where does training data come from? How is it labeled? Label noise handling?
- Train/validation/test split — how did you avoid leakage?
- Class imbalance — what did you do about it?
- Featurization: how are features computed at training time vs. serving time? Skew?

## Modeling (classical ML)

- Bias/variance in the model you chose; how did you diagnose overfitting?
- Feature importance — which method, and what were its known blind spots?
- Regularization choice and why.
- Cross-validation strategy; why that one?

## Evaluation

- Choice of metric — why *this* one? What does it hide?
- Precision vs. recall tradeoff in the context of the actual product decision.
- Offline vs. online metrics — how did they correlate?
- A/B testing: sample size, sequential testing pitfalls, novelty effects.

## Drift and monitoring in production

- Data drift vs. concept drift — how do you detect each?
- What's the retraining trigger — schedule, drift signal, performance drop?
- Rollback plan when a new model is worse than the old one.
- Serving latency budget — how tight, and what did you drop to fit?

## LLM / retrieval / agents

- RAG pipeline: chunking strategy, embedding choice, retrieval scoring, reranking. Why each choice?
- Chunk overlap vs. chunk size — the tradeoff.
- Grounding vs. hallucination — how do you evaluate whether an answer is actually supported by the retrieved context?
- Prompt evaluation — how do you know a prompt change didn't regress on cases you cared about? What's the eval set?
- Tool use / function calling — how do you handle a tool call that fails or returns garbage?
- Multi-step agents — how do you bound cost and iterations? What's the failure mode when the agent loops?
- Guardrails: injection prevention, output validation, refusal behavior.

## LLM systems

- Token accounting: input vs. output tokens, cache tokens, cost per call.
- Streaming vs. non-streaming — implications for UX and backend.
- Prompt caching — when it earns its keep; when it doesn't.
- Latency budget for an agent call chain; where the wall-clock time goes.
- Fine-tuning vs. prompt engineering vs. RAG — when does each win?

## Deployment

- Batch vs. online serving — how did you choose?
- Model versioning — how do you roll forward and back?
- Shadow deployments, canary, A/B — which pattern for which risk?
- Feature store: do you have one, why or why not, what's the cost of not having one?

## Evaluation of an LLM feature (product-facing)

- What's the "did the model do the job" signal — user thumbs, downstream metric, human eval?
- How do you handle the fact that "good answer" is subjective?
- LLM-as-judge — when is it fine, when is it dangerous?
- Regression testing — how do you know the new prompt/model didn't break yesterday's good behavior?

---

## How to pick from this list

- Anchor to the candidate's actual project. If they shipped a RAG system, drill retrieval + eval + drift, not classical ML.
- The highest-signal areas for most LLM candidates are: **eval discipline**, **grounding / hallucination handling**, and **cost/latency reasoning**. If in doubt, start there.
- Bluff risk is high in this domain. Push for specifics: which model, which embedding, which eval set, which metric. Vague answers = drill down or move to fundamentals.
