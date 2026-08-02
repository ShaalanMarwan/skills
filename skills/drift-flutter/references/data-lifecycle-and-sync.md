# Data lifecycle and synchronization

## Existing and pre-populated databases

Preserve the exact existing database directory and filename when adopting Drift from sqflite, sqlite3, or another wrapper. A new path creates a new file and looks like data loss. Import existing `CREATE TABLE`, index, trigger, and view statements into `.drift` files when that is the easiest source of truth; put pragmas and other setup statements in `beforeOpen`.

Use `LazyDatabase` or `drift_flutter` initialization options to copy a bundled database only when the destination does not exist. Validate the bundled schema and its `user_version` against the application migration strategy.

WAL databases have associated `-wal` and `-shm` files. Copying only the main file may omit recent transactions. Checkpoint or close the source cleanly before backup, and handle auxiliary files when replacing databases.

## Backup and restore

On native SQLite, `VACUUM INTO` can produce a consistent standalone file. Restore only while the application database is closed, validate the incoming schema/version, retain a recoverable copy of the current database, and reopen through the normal owner. Web uses probe/export and initialization APIs with different storage constraints; WAL database files cannot be initialized directly on web.

## Synchronization

Drift does not implement server synchronization by itself. Manual sync typically needs durable change tracking, conflict resolution, retries, tombstones, server validation, and idempotency. Network calls must not occur inside long-lived database transactions.

Document the consistency model before implementing sync:

- source of truth and merge/conflict rules;
- identifier generation;
- deletion/tombstone retention;
- upload/download cursors and retry semantics;
- authorization and tenant boundaries;
- schema compatibility across client versions;
- how remote changes notify local Drift streams.

PowerSync integrates with Drift and supports local/remote change flows, but uploads and backend validation still require application decisions. libSQL replication is another executor choice. Remote-only clients such as Hrana do not automatically make a local stream react to writes from unrelated clients. Treat old ElectricSQL guidance in the docs as outdated unless current Dart support is independently verified.

## Tracing

Use `logStatements` for development-only visibility or `QueryInterceptor` for scoped tracing and timing. Redact bind parameters that may contain secrets or user data. Measure slow operations before adding indexes, read pools, caching, or retries.
