---
name: powersync-flutter
description: Design, implement, self-host, migrate, test, operate, and debug PowerSync in Dart and Flutter applications. Use when a task involves PowerSync, offline-first or local-first Flutter data, Sync Streams or legacy Sync Rules, PowerSyncDatabase, PowerSyncBackendConnector, uploadData, fetchCredentials, self-hosted PowerSync Service, Supabase or custom database replication, or integrating PowerSync with an existing Drift database through drift_sqlite_async.
---

# PowerSync for Flutter

Use this skill as a workflow, not as a snippet catalog. PowerSync has two independent data paths: the Service replicates backend data down to local SQLite, while the app's backend connector uploads local mutations through the application's backend. A working read path does not imply a working write path.

## Start with project detection

Run the read-only detector from the Flutter project or pass its path:

```bash
bash scripts/detect_flutter_stack.sh [project-directory]
```

Use its `recommended_client_path` result:

- `drift-adapter`: preserve Drift and connect it to the PowerSync database with `drift_sqlite_async`. Read [references/drift-integration.md](references/drift-integration.md) and [references/flutter-client.md](references/flutter-client.md).
- `native-powersync`: use the PowerSync Dart API directly. Read [references/flutter-client.md](references/flutter-client.md).
- `drift-adapter-present`: inspect the existing adapter and extend it instead of creating a second database connection.

Never open the same PowerSync database file independently through Drift. The adapter shares PowerSync's `sqlite_async` connection, locks, transactions, and external update notifications.

## Establish scope before changing anything

Determine all of the following from the project or ask the operator:

1. PowerSync Cloud or self-hosted PowerSync.
2. Source database: Postgres/Supabase, MongoDB, MySQL, SQL Server, or Convex.
3. Existing app backend and authentication provider.
4. New deployment or existing instance; for an existing instance, identify dev, staging, or production.
5. Read-only sync or bidirectional writes.

Do not assume Supabase. Do not mutate or deploy an existing instance until its exact target and environment are confirmed. Default to changing only `sync-config.yaml`; require explicit authorization before changing `service.yaml`, auth, storage, replication, or infrastructure.

## Follow the implementation sequence

1. **Inspect first.** Run the detector; inspect `pubspec.yaml`, database code, backend APIs, auth, existing `powersync/` config, schema, and tests.
2. **Choose the service path.** For Cloud use the Cloud workflow; for self-hosting read [references/self-hosting.md](references/self-hosting.md) completely before editing infrastructure.
3. **Prepare the source database.** Configure its CDC/replication mechanism, a least-privilege replication identity, and only the tables required by sync. Read [references/source-databases-and-auth.md](references/source-databases-and-auth.md).
4. **Define secure Sync Streams.** Use `config: edition: 3` and Sync Streams for new work. Treat subscription and connection parameters as client-controlled; enforce authorization with signed auth claims or server-side relationship queries. Read [references/sync-streams.md](references/sync-streams.md).
5. **Validate the service before client code.** Confirm database connectivity, active sync config, client auth, source replication, endpoint, and a representative user with the Sync Diagnostics Client or CLI.
6. **Define the client schema.** Match names and SQLite storage classes emitted by Sync Streams. PowerSync supplies the text `id`; do not declare it in a native PowerSync `Table`. With Drift, declare `id` because Drift needs the typed column, but keep the matching PowerSync schema separate.
7. **Implement the Flutter database lifecycle.** Initialize exactly one `PowerSyncDatabase` per file, connect after auth, expose status and watch streams, and close it with the application's lifecycle. Read [references/flutter-client.md](references/flutter-client.md).
8. **Implement the write path.** Make `uploadData` idempotent and synchronous with source-database commits. Complete a CRUD transaction or batch only after successful handling. Read [references/writes-conflicts-and-consistency.md](references/writes-conflicts-and-consistency.md).
9. **Handle logout deliberately.** Use `disconnectAndClear()` on logout or user switch when another user must not see cached data. Use `disconnect()` only when retaining the local cache is intentional and safe.
10. **Test offline behavior.** Cover first sync, writes while offline, reconnection, token refresh, duplicate upload delivery, rejected writes, conflicts, logout, app restart, schema changes, and stream subscription lifecycle.
11. **Add operational checks.** For production or self-hosting, configure health probes, metrics, replication-lag monitoring, compaction, backups/config versioning, capacity, TLS, secret management, and rollout procedures. Read [references/operations-testing-and-debugging.md](references/operations-testing-and-debugging.md).

## Use the CLI safely

Prefer the PowerSync CLI for scaffolding, validation, schema generation, status, token generation, and supported deployments. Do not invent config keys or copy stale examples; start with CLI-generated files and validate them.

- `powersync login` authenticates PowerSync Cloud. It is not the login path for a self-hosted service.
- Before `deploy`, `stop`, `destroy`, `compact`, `link --create`, or `pull instance`, identify and confirm the target.
- `powersync pull instance` overwrites local service and sync config. Preserve local work before using it.
- Prefer a scoped sync-config deployment when only streams changed.
- Never embed source database passwords, JWT signing secrets, admin tokens, or encryption keys in version control or client code.

## Apply non-negotiable design rules

- Read all application data from local SQLite; do not add network reads that bypass the local source of truth unless the product explicitly requires them.
- Use lowercase table and column identifiers and a single text primary key named `id` for synced rows.
- Use UUIDs or another client-generatable text ID for offline inserts. If the backend requires sequential IDs, map them separately.
- Keep PowerSync's client schema, Sync Streams output, backend schema, and Drift model aligned.
- Use auth parameters for authorization. A filter containing only `subscription.parameter(...)` is not authorization.
- Do not expect source-database RLS to filter the replication read path. Apply client visibility in Sync Streams; enforce writes again in the backend.
- Do not use `GROUP BY`, `ORDER BY`, `LIMIT`, aggregation, nondeterministic time, or random functions in Sync Streams. Perform presentation queries locally.
- Do not store large files in synced rows. Sync metadata and use the attachment queue with object storage.
- Treat the upload queue as blocking FIFO. A permanently failing head operation prevents later writes and checkpoint advancement.
- Return success for handled validation conflicts and communicate rejection through response data or a synced errors table. Reserve thrown errors/non-2xx behavior for genuinely retryable failures or bugs requiring intervention.
- Make uploaded operations idempotent because delivery can repeat.
- Do not call `transaction.complete()` until every operation represented by it is safely applied, deliberately rejected, or durably dead-lettered.
- Do not create two local caches for the same server data. With Riverpod/BLoC/provider, expose database futures and streams rather than duplicating synced state.

## Load detailed guidance only when needed

| Task | Read |
|---|---|
| Architecture, buckets, checkpoints, consistency | [references/architecture.md](references/architecture.md) |
| Flutter SDK setup, queries, lifecycle, web, state management | [references/flutter-client.md](references/flutter-client.md) |
| Existing Drift app or `drift_sqlite_async` | [references/drift-integration.md](references/drift-integration.md) |
| Stream design, subscriptions, parameters, SQL constraints | [references/sync-streams.md](references/sync-streams.md) |
| Backend connector, uploads, validation, conflict resolution | [references/writes-conflicts-and-consistency.md](references/writes-conflicts-and-consistency.md) |
| Source database, backend, JWT, Supabase and other auth | [references/source-databases-and-auth.md](references/source-databases-and-auth.md) |
| Docker, CLI, service configuration, ECS/EKS/Coolify/Railway | [references/self-hosting.md](references/self-hosting.md) |
| Tests, diagnostics, monitoring, upgrades, schema rollout | [references/operations-testing-and-debugging.md](references/operations-testing-and-debugging.md) |
| Attachments, encryption, JSON, FTS, raw tables, background sync | [references/advanced-client-features.md](references/advanced-client-features.md) |
| Documentation audit and page inventory | [references/documentation-coverage.md](references/documentation-coverage.md) |
| Primary sources and repositories | [references/official-sources.md](references/official-sources.md) |

When guidance may have changed, consult the primary links in `official-sources.md` and the current package changelogs before choosing version-specific APIs.
