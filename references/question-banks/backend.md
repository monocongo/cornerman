# Question Bank — Backend

**These are seed topics, not a script.** The interviewer follows the candidate's answers. Use this list when the candidate's project maps to one of these areas and you need somewhere to start drilling — then abandon the list and chase whatever they said.

Every topic below has the escalation ladder implicit:
1. **Conceptual** — what is it?
2. **Applied** — why did you choose it in your project?
3. **Edge / failure** — what breaks under Z?

---

## Databases (relational)

- Indexes: B-tree vs. hash, composite index order, covering indexes; when does an index hurt?
- Isolation levels: what actually happens at READ COMMITTED vs. REPEATABLE READ vs. SERIALIZABLE; phantom reads, write skew.
- Transactions: 2PC, saga; when to reach for each.
- Query plans: how to read one; what does a full scan mean; when is it fine.
- Replication: sync vs. async, read replicas, replication lag, read-your-writes.
- Sharding: choosing a shard key; resharding pain; cross-shard queries.
- Migrations: online vs. offline; adding a NOT NULL column to a huge table safely; backfills.

## Databases (NoSQL / other)

- When would you pick NoSQL over SQL — and be specific about which NoSQL.
- Key-value vs. document vs. wide-column vs. graph — what workloads?
- Eventual consistency: what does "eventual" mean operationally?
- Modeling: designing a data model for the access pattern, not the entities.

## Caching

- Cache invalidation strategies: TTL, write-through, write-around, write-back.
- Stampede protection (thundering herd, request coalescing, probabilistic early expiration).
- Where should the cache live: in-process, sidecar, external cluster? Tradeoffs.
- Consistency vs. staleness — what's acceptable in your project?

## Message queues / streaming

- Kafka: partitions, consumer groups, offsets, retention.
- At-least-once vs. at-most-once vs. exactly-once — what does each require?
- Idempotent producers, transactional consumers.
- Backpressure: what happens when the consumer can't keep up?
- Ordering guarantees — within a partition vs. across partitions.
- Dead-letter queues, poison messages, retries.

## APIs

- REST vs. gRPC vs. GraphQL — when each earns its keep.
- Idempotency for POST/PUT/DELETE; idempotency keys.
- Versioning: URL-versioning vs. header-versioning vs. never-break; deprecation policy.
- Pagination: offset vs. cursor; why cursor wins at scale.
- Rate limiting: token bucket, leaky bucket, sliding window; per-user vs. per-IP.

## Auth

- Session-based vs. token-based; where the tradeoff lives.
- JWT: what's in it, what's the risk, when's a revocation list needed.
- OAuth 2 flows: auth code vs. client credentials vs. device flow; when to use each.
- Refresh tokens: rotation, revocation.

## Concurrency

- Threads vs. async I/O; when async isn't a win.
- Locks: optimistic vs. pessimistic; row-level vs. table-level.
- Race conditions in a "read-then-write" flow; how to make it atomic.
- Deadlocks: how they happen, how to detect, how to avoid.

## Distributed systems basics

- CAP: what the letters actually mean; why "we chose CP" is usually a shallow answer.
- Consensus: Raft/Paxos at a "why do we need it" level; leader election.
- Idempotency and retries in a distributed call chain.
- Circuit breakers, bulkheads, timeouts as first-class design.

## Observability

- Logs, metrics, traces — what each is for; what happens if you only have one.
- Cardinality traps in metrics.
- SLOs vs. SLAs vs. SLIs.
- Debugging a slow request in production — what do you check first?

---

## How to pick from this list

- Look at the candidate's project. Match to the closest area(s).
- Start at rung 1 only if you're not sure they know it. Otherwise start at rung 2 (applied).
- One good drill on one topic > touching five topics. Depth reveals; breadth doesn't.
