# Architecture and consistency

## Contents

- System boundary
- Read and write paths
- Client database internals
- Buckets and protocol
- Checkpoints and consistency
- Design consequences

## System boundary

PowerSync consists of three application-owned or operated layers:

1. **Source database**: The authoritative backend database: Postgres, MongoDB, MySQL, SQL Server, or Convex.
2. **PowerSync Service**: Replicates source changes through CDC, evaluates Sync Streams, persists partitioned operation history in a separate bucket-storage database, authenticates clients, and streams applicable operations.
3. **Client SDK**: Manages local SQLite, applies downloaded checkpoints, records local changes in a blocking upload queue, and asks an application-defined connector for credentials and upload behavior.

The application backend remains part of the architecture. PowerSync Service is the read/downstream path; it does not automatically apply client writes to the source database.

```text
source database --CDC--> PowerSync Service --sync stream--> local SQLite
       ^                                                     |
       |                                                     v
       +--- application backend <-- uploadData() <-- upload queue
```

## Read and write paths

### Read path

- The Service reads database changes through logical replication, change streams, binlog, CDC, or document deltas.
- Sync Streams determine which transformed rows enter each user's internal buckets.
- Clients download operation history and apply only complete checkpoints.
- The app always queries local SQLite, online or offline.
- Watch queries re-run when dependent local tables change.

### Write path

- A local `INSERT`, `UPDATE`, or `DELETE` changes SQLite immediately and atomically appends a `PUT`, `PATCH`, or `DELETE` entry to `ps_crud`.
- The SDK invokes `uploadData()` while connected.
- `uploadData()` calls the application backend (or a provider API such as Supabase/Convex) to commit to the source database.
- The Service later observes the committed change through CDC and sends it back in a checkpoint.
- The local optimistic state is reconciled with the server-authoritative state.

Do not acknowledge an upload before its source-database write is durable. An asynchronous backend queue can create disappearance/reappearance glitches because the client may advance before CDC contains the write.

## Client database internals

PowerSync's default client tables are SQLite views over schemaless JSON storage. Important internal tables include:

| Internal object | Purpose |
|---|---|
| `ps_data__<table>` | Materialized server-backed row state as JSON |
| `ps_data_local__<table>` | Local-only table data |
| client table view | Casts selected JSON properties into the declared SQLite schema |
| `ps_untyped` | Synced data not yet present in the client schema |
| `ps_oplog` | Downloaded bucket operation history awaiting/checkpointed application |
| `ps_crud` | Blocking FIFO upload queue for local mutations |
| `ps_buckets` | Bucket and checkpoint metadata |
| `ps_migrations` | Client schema application history |

Default views make additive schema changes relatively tolerant: the protocol is schemaless and a new client view can expose existing JSON properties. They also mean client-side foreign keys and `ON DELETE CASCADE` are not automatically available. Use explicit transactional deletes, or use raw tables only when their extra control justifies custom DDL, migrations, and CRUD triggers.

## Buckets and protocol

Buckets are internal partitions of ordered row operations. Sync Streams create them implicitly from query and parameter values. Shared buckets deduplicate common data across users, and each bucket retains recent operation history for incremental catch-up.

The protocol exchanges:

1. Client JWT, parameters, known bucket operation positions, and checksums.
2. A checkpoint declaration with expected buckets/checksums.
3. Missing operations per bucket.
4. Checkpoint completion.

The client atomically advances only after all data for a checkpoint is present and valid. Checksums detect mismatched or corrupt bucket state; a failed bucket is removed and downloaded again.

Overlapping buckets may contain the same row. A row is removed locally only after it has been removed from every active/cached bucket that supplies it.

## Checkpoints and consistency

PowerSync targets causal+ consistency:

- A checkpoint corresponds to a consistent source-database position and never exposes half of a committed server transaction.
- Local changes overlay the last server checkpoint.
- While local mutations remain queued, ordinary checkpoint advancement is delayed so the client does not need to resolve conflicts locally.
- After uploads empty, the client requests a write checkpoint. When CDC has reached the committed writes, reconciliation can advance.
- The server/backend decides validation and conflict behavior; the eventual client state matches the authoritative source state.

Priority-zero streams are a special case in prioritized syncing and may relax the ordinary cross-priority checkpoint relationship. Consult current prioritized-sync documentation before relying on them.

## Design consequences

- Model the local SQLite database as the app's source of truth, not a cache behind network repositories.
- Design the write endpoint for idempotent retries and transaction boundaries.
- Keep write validation in the backend even when Sync Streams correctly restrict reads.
- Size initial sync by per-user rows and buckets, not only total source-database size.
- Prefer on-demand streams and TTLs when a user does not need the entire working set offline.
- Monitor both replication lag (source to Service) and client status (Service to device); they describe different failures.
- Treat a stuck upload queue as a consistency incident because it also delays normal checkpoint progress.

Primary documentation: [architecture overview](https://docs.powersync.com/architecture/architecture-overview), [client architecture](https://docs.powersync.com/architecture/client-architecture), [consistency](https://docs.powersync.com/architecture/consistency), [protocol](https://docs.powersync.com/architecture/powersync-protocol), and [service architecture](https://docs.powersync.com/architecture/powersync-service).
