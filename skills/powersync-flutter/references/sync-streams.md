# Sync Streams

## Contents

- New-project baseline
- Stream lifecycle
- Parameter security
- Query patterns
- SQL and schema constraints
- Priorities, TTL, and compatibility
- Legacy Sync Rules migration
- Review checklist

## New-project baseline

Use Sync Streams with edition 3 for new projects:

```yaml
config:
  edition: 3

streams:
  my_lists:
    auto_subscribe: true
    query: SELECT * FROM lists WHERE owner_id = auth.user_id()

  list_todos:
    query: |
      SELECT * FROM todos
      WHERE list_id = subscription.parameter('list_id')
        AND list_id IN (
          SELECT id FROM lists
          WHERE owner_id = auth.user_id()
             OR id IN (
               SELECT list_id FROM list_shares
               WHERE shared_with = auth.user_id()
             )
        )
```

Use `query` for one output table/query and `queries` to group several related outputs under one subscription. A stream can also define reusable CTEs with `with:`. Validate configuration with the CLI before applying it.

## Stream lifecycle

- `auto_subscribe: true` starts the stream on every authenticated connection. Use it for small reference sets and data that must always be offline-ready.
- Without auto-subscribe, the client subscribes with `db.syncStream(name, parameters).subscribe()`.
- A subscription has a distinct identity for its stream name and parameter set.
- Unsubscribe when a feature no longer needs live sync. Cached rows remain for the subscription TTL; the documented default is 24 hours.
- Multiple buckets may supply the same row. Unsubscribing one stream does not remove a row still supplied by another.
- Generated typed wrappers are preferable to raw stream strings when available; wrong names/keys can otherwise fail silently with missing data.

## Parameter security

Sync Streams expose three parameter classes:

| Parameter | Origin | Security use |
|---|---|---|
| `auth.user_id()` / `auth.parameter('claim')` | Signed JWT | Trusted authorization input after JWT verification |
| `subscription.parameter('key')` | Client per subscription | Selection only; client-controlled |
| `connection.parameter('key')` | Client at connection | Session-wide selection only; client-controlled |

Never authorize data with an unverified subscription/connection parameter alone. Bind it to signed identity or a relationship query:

```sql
WHERE project_id = subscription.parameter('project_id')
  AND project_id IN (
    SELECT project_id FROM project_members
    WHERE user_id = auth.user_id()
  )
```

The configuration may warn about client-controlled parameters. Do not silence warnings with `accept_potentially_dangerous_queries: true` until the authorization path is reviewed.

Source-database RLS does not automatically filter logical replication for each client. Sync Streams control the replicated read visibility; the backend must separately enforce write authorization.

## Query patterns

### Global reference data

```yaml
categories:
  auto_subscribe: true
  query: SELECT * FROM categories WHERE active = true
```

This data reaches every client. Keep it genuinely public/tenant-neutral and small.

### Tenant membership

```yaml
tenant_data:
  auto_subscribe: true
  with:
    allowed_tenants: |
      SELECT tenant_id FROM tenant_members
      WHERE user_id = auth.user_id()
  queries:
    - SELECT * FROM tenants WHERE id IN allowed_tenants
    - SELECT * FROM projects WHERE tenant_id IN allowed_tenants
```

CTEs cannot reference other CTEs; use nested subqueries when chaining relationships. Edition 3 permits global CTEs, but global CTE names must not shadow source table names.

### On-demand detail

```yaml
project_detail:
  query: |
    SELECT * FROM tasks
    WHERE project_id = subscription.parameter('project_id')
      AND project_id IN (
        SELECT project_id FROM project_members
        WHERE user_id = auth.user_id()
      )
```

### Join-based authorization

```sql
SELECT comments.*
FROM comments
JOIN issues ON comments.issue_id = issues.id
JOIN project_members ON issues.project_id = project_members.project_id
WHERE project_members.user_id = auth.user_id()
```

Only inner joins are supported; output columns must come from a single source table and join conditions must use supported equality relationships.

### Arrays in JWT claims

```sql
SELECT * FROM projects WHERE id IN auth.parameter('project_ids')
```

`json_each()` and subquery forms are available for more explicit expansion.

### Column projection and transforms

```sql
SELECT
  id,
  item_number::text AS item_number,
  metadata ->> 'description' AS description,
  unixepoch(created_at) AS created_at
FROM items
```

Projection reduces transfer and defines the exact client schema. Remember that removing a column affects old app versions.

## SQL and schema constraints

Sync Stream SQL is deterministic selection/transformation, not general reporting SQL.

Supported building blocks include `SELECT`, `WHERE`, subqueries, `IN`, inner joins, CTEs, JSON functions, limited scalar functions, arithmetic/comparison/logical operators, casts, and `CASE`.

Do not use:

- `GROUP BY`, aggregation, `ORDER BY`, `LIMIT`, or set operations such as `UNION`;
- random, current-time, or other nondeterministic functions;
- arbitrary external state;
- joins that emit columns from more than one output table;
- unsupported outer/non-equality joins.

Every synced source table needs one text-compatible primary key named `id`. Alias/transform another identifier if necessary; MongoDB commonly aliases `_id AS id`. Use lowercase identifiers to avoid cross-database case problems.

Client-visible SQLite types reduce to text, integer, real, blob, or null. Align stream transforms with the PowerSync and Drift schemas.

## Priorities, TTL, and compatibility

- Lower numeric priority means earlier sync. Use priorities to deliver shell/reference/working data before large history.
- Preserve consistency relationships when splitting related tables across priorities; priority zero has special semantics and requires careful review.
- Subscription TTL trades storage for navigation latency. Sensitive or large detail data may need a short/zero TTL; frequently revisited data benefits from a warm cache.
- Maintain streams/columns compatible with multiple deployed app versions. Add before use, keep old outputs during rollout, then remove only after old clients are retired.
- Each parameterized result contributes internal buckets; review the documented per-client bucket limit and avoid unbounded per-row subscription fan-out.
- For time-windowed sync, do not use current-time functions. Model a deterministic cutoff parameter/data field and update subscriptions/config deliberately.

## Legacy Sync Rules migration

Sync Rules are legacy. For an existing project:

1. Inventory bucket definitions, request/JWT parameters, client parameters, global buckets, and many-to-many patterns.
2. Generate a draft with the Dashboard migration action or `powersync migrate sync-rules`.
3. Replace request/bucket syntax with auth/subscription/connection parameters and Stream queries.
4. Decide which former always-on buckets need `auto_subscribe: true`.
5. Add explicit client subscriptions for on-demand streams.
6. Validate each representative user with diagnostics and run mixed-client compatibility tests.
7. Deploy alongside the current serving config; PowerSync processes the new version before clients transition.

## Review checklist

- [ ] `config.edition` is current and valid.
- [ ] Each stream has a bounded business purpose.
- [ ] Every client-controlled parameter has an authorization condition.
- [ ] Global/auto-subscribed data is intentionally visible and sized.
- [ ] Output names/types match client schemas.
- [ ] IDs are lowercase, text-compatible, and named `id`.
- [ ] Query syntax stays within the supported deterministic subset.
- [ ] Local indexes cover UI predicates and joins.
- [ ] Subscription handles, TTLs, and priorities have owners.
- [ ] Old app versions remain compatible.
- [ ] Representative JWTs and subscriptions pass diagnostics.

Primary documentation: [Sync Streams overview](https://docs.powersync.com/sync/streams/overview), [parameters](https://docs.powersync.com/sync/streams/parameters), [queries](https://docs.powersync.com/sync/streams/queries), [client usage](https://docs.powersync.com/sync/streams/client-usage), [supported SQL](https://docs.powersync.com/sync/supported-sql), and [migration](https://docs.powersync.com/sync/streams/migration).
