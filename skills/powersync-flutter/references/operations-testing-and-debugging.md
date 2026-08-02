# Operations, testing, and debugging

## Contents

- Test pyramid
- Diagnostics workflow
- Self-hosted probes and metrics
- Replication and storage operations
- Schema and client rollout
- Production readiness

## Test pyramid

### Client unit/integration tests

Use temporary per-test database paths and close/delete them after each test. Current PowerSync 2.x build hooks may provide native binaries differently from older docs; follow the installed package's test setup and verify the SQLite core extension loads in the test process.

Test:

- schema application and representative queries;
- insert/update/delete queue creation;
- Drift mappings, generated queries, migrations, and external update notifications;
- local-only behavior;
- subscription creation, readiness, unsubscribe, and TTL;
- `disconnect()` versus `disconnectAndClear()`;
- database reopen/restart.

### Connector contract tests

Use a fake/staging backend and verify:

- duplicate operations are idempotent;
- transaction grouping is preserved;
- `.complete()` is called only after handled durability;
- temporary failures remain queued and retry;
- permanent validation advances the queue through a deliberate handled outcome;
- token refresh, expiry, invalidation, and offline recovery;
- table/row authorization and payload allowlists.

### End-to-end/offline tests

Run two clients plus the source database:

1. First sync from a clean install.
2. Offline read and write, process kill, restart, reconnect.
3. Concurrent same-field and different-field edits.
4. Delete versus offline update.
5. Large catch-up after prolonged offline use.
6. Stream authorization for allowed and forbidden IDs.
7. User switch/logout with pending uploads.
8. Old/new app versions during backend/stream/schema rollout.
9. Service restart, replica failover, auth/JWKS outage, and bucket storage interruption.
10. Migration between PowerSync endpoints and resulting automatic full resync.

## Diagnostics workflow

Classify the failing path before editing code:

### No downloaded data

1. Verify endpoint and a fresh JWT/audience.
2. Verify the source connection and CDC/publication.
3. Verify active/deploying Sync Streams and initial replication.
4. Test the same JWT/subscription in the Sync Diagnostics Client.
5. Inspect stream status/bucket count and exact parameter values.
6. Compare stream output names/types with the client schema.
7. Inspect `ps_untyped`, `ps_oplog`, and client status using DevTools/database diagnostics.

### Local write visible but not uploaded

1. Inspect `ps_crud` and `uploadError`.
2. Confirm sync is connected; uploads do not run while disconnected.
3. Confirm `uploadData()` obtains a transaction/batch and completes it.
4. Check backend response classification and server logs.
5. Verify auth identity and write authorization.

### Backend write succeeds but UI reverts

1. Confirm the endpoint did not acknowledge before source commit.
2. Confirm CDC publication includes the table and replication is healthy.
3. Check stream authorization/output for the modified row.
4. Inspect type/column transforms and conflict/validation rules.

### Drift watch query does not update

1. Confirm Drift uses `SqliteAsyncDriftConnection` around the same PowerSync instance.
2. Confirm the query's table names match PowerSync update notifications.
3. Add `transformTableUpdates` only for actual local table/view-name mismatches.
4. Confirm the adapter and watched query are not closed/disposed.
5. Reproduce a Drift-originated and a PowerSync-originated change separately.

### Excessive storage or slow sync

1. Break down the client SQLite file (`ps_data__`, `ps_oplog`, indexes, local tables).
2. Review rows/buckets per user, TTLs, auto-subscriptions, and initial-sync size.
3. Compact Service buckets and run SQLite maintenance only when documented/safe.
4. Add local indexes for client query predicates.
5. Reduce stream columns/rows; use on-demand subscriptions and priorities.

Use error codes by family: `PSYNC_Rxxxx` indicates sync-config/query problems; `PSYNC_Sxxxx` indicates Service, replication, auth, capacity, or storage issues. Always inspect the code's structured details.

## Self-hosted probes and metrics

Available health endpoints:

- `GET /probes/startup`: process completed startup.
- `GET /probes/liveness`: process remains alive.

For deeper state, configure a strong admin token and use `powersync status` or the diagnostics API. Inspect source connections, active and deploying sync configs, initial replication, slot name/status, replication lag bytes, safe WAL size, and errors.

Enable Prometheus:

```yaml
telemetry:
  prometheus_port: 9090
```

Scrape every API/replication process separately. High-value signals include concurrent connections, replication lag, replicated/synced bytes and rows/operations, and replication/operation/parameter storage sizes. Alert on sustained lag, near-capacity API pods, WAL budget, repeated auth/stream errors, stalled config deployment, and bucket storage growth.

## Replication and storage operations

- Postgres logical slots retain WAL. Drop only confirmed-unused inactive slots. If a slot is `lost`, increase the relevant WAL retention limit, drop the invalid slot, and restart/re-snapshot as documented.
- A new stream config may create a new slot while the old config remains active; provision slot and WAL headroom.
- Run bucket compaction daily and after large maintenance/import operations. Managed Cloud compacts automatically; self-hosted deployments own the job.
- Back up source data normally. Bucket storage can be reconstructed from the source but losing it forces re-replication and client resync; back it up when recovery time matters.
- Use JSON structured logs and custom app metadata to correlate user/client sessions without logging secrets or sensitive row contents.

## Schema and client rollout

PowerSync's schemaless protocol makes additive changes tolerant, but client views and app code still need coordinated rollout:

1. Add backend columns/tables and CDC/publication access.
2. Deploy streams that preserve existing output while adding new output.
3. Wait for initial replication/deployment completion.
4. Release clients whose PowerSync and Drift schemas understand the new output.
5. Monitor mixed versions.
6. Remove old columns/streams only after old clients are retired.

For destructive source changes, understand the database-specific CDC behavior. Avoid renames that old clients interpret as deletion/addition without a compatibility window.

## Production readiness

- [ ] Representative-user diagnostics pass before release.
- [ ] Sync config and service config are validated and reviewed.
- [ ] Upload endpoint load, idempotency, and retry behavior are tested.
- [ ] Client database and per-user sync volume fit supported limits with headroom.
- [ ] Source publication excludes unnecessary high-write tables.
- [ ] Replication lag, WAL, connections, storage, errors, and upload failures alert.
- [ ] Self-hosted compaction, migrations, probes, TLS, secrets, and scaling are automated.
- [ ] Logout/data retention and device encryption policies are documented.
- [ ] Rollback preserves compatibility across source schema, streams, service, and clients.
- [ ] Beta/alpha features used by the design are accepted explicitly.

Primary documentation: [troubleshooting](https://docs.powersync.com/debugging/troubleshooting), [error codes](https://docs.powersync.com/debugging/error-codes), [client database diagnostics](https://docs.powersync.com/maintenance-ops/client-database-diagnostics), [production readiness](https://docs.powersync.com/maintenance-ops/production-readiness-guide), [replication lag](https://docs.powersync.com/maintenance-ops/replication-lag), and [self-host diagnostics](https://docs.powersync.com/maintenance-ops/self-hosting/diagnostics).
