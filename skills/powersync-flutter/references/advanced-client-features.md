# Advanced client features

## Contents

- Attachments
- Encryption
- JSON, arrays, and custom types
- Raw tables
- Full-text search and extensions
- Background sync
- Local-only and pre-seeded databases
- Pagination and large datasets

## Attachments

Do not put large images, video, PDFs, or base64 blobs in synced database rows. Use a metadata + object-storage pattern:

1. Save the file locally and create local attachment metadata.
2. Upload/download through a storage adapter (S3, Supabase Storage, R2, etc.), preferably with short-lived signed URLs.
3. Sync only the attachment ID/reference in the application row.
4. Watch synced references on other devices and queue needed downloads.
5. Archive/delete files when no model row references them.

PowerSync's built-in Flutter attachment helpers replaced the deprecated standalone helper package. Confirm the installed SDK's current alpha API and migration notes. The attachment queue's metadata table is local-only; the application model provides cross-device references.

## Encryption

Transport uses TLS. For Flutter database encryption at rest, current PowerSync 2.x supports `EncryptionOptions` with SQLite3MultipleCiphers or SQLCipher on compatible platforms:

```dart
final db = PowerSyncDatabase(
  schema: schema,
  path: path,
  encryption: EncryptionOptions(key: keyFromSecureStorage),
);
```

Native builds select an encrypted SQLite implementation through Dart build hooks; web encryption uses the matching encrypted WASM asset/setup command. Store keys in platform secure storage, never source/assets. Plan key loss, rotation, logout, backup, and app-upgrade behavior. Database encryption does not replace authorization or end-to-end field encryption.

For E2EE, sync ciphertext and decrypt in memory or into carefully managed local-only/raw data. Keep searchable plaintext leakage and key distribution in the threat model.

## JSON, arrays, and custom types

PowerSync transfers JSON/JSONB/native arrays as JSON text. Declare text on the client and parse/map deliberately. Use SQLite JSON functions (`json_extract`, `->`, `->>`, `json_each`) for local queries, and supported JSON functions in streams for filtering/transforms.

Other source types must map to SQLite-compatible text/integer/real/blob. Common strategies:

- timestamps → ISO text or epoch integer;
- decimals beyond safe floating precision → text;
- UUID → text;
- PostGIS geometry → GeoJSON/WKT or coordinate columns through supported stream functions;
- binary → base64 text only for small values; use attachments for files.

Advanced schema options can track previous values and metadata for custom writes/conflict resolution. Do not enable them without a backend consumer and tests.

## Raw tables

Default PowerSync tables are JSON-backed views. Choose raw tables only for native SQLite features, full schema control, local-only columns, or proven performance needs.

With raw tables you must:

- create and migrate physical tables before connecting;
- define how downloaded PUT/DELETE operations apply;
- add insert/update/delete triggers that write to the `powersync_crud` virtual table when local writes should upload;
- preserve update notifications for reactive queries;
- plan data deletion and schema upgrades;
- accept incompatibilities such as unavailable high-performance diff features.

Prefer inferred raw-table statements/triggers where supported, then inspect generated behavior. In a Drift app, assign physical DDL/migration ownership explicitly to avoid PowerSync and Drift creating the same object.

## Full-text search and extensions

FTS5 is local derived state:

- create virtual tables after the PowerSync database exists;
- update them with triggers/maintenance tied to underlying PowerSync changes;
- rebuild after schema changes or database clear;
- do not sync the FTS index itself;
- query locally through PowerSync or Drift.

SQLite extensions vary by platform. Verify build/link/load support for Dart/Flutter, especially web and mobile app-store constraints. Treat vector/spatial/custom tokenizer availability as a deployment compatibility choice, not merely a SQL choice.

## Background sync

Flutter background execution is platform-limited. The official guide demonstrates Workmanager:

- mark the entry point with `@pragma('vm:entry-point')`;
- initialize the database/connector in the background process/isolate;
- coordinate so only one instance actively syncs a database endpoint;
- perform bounded work within OS time/battery rules;
- upload pending mutations deliberately if the SDK connection window is short;
- close the database before task completion;
- test Android and iOS separately—iOS scheduling is constrained and not guaranteed.

Never promise continuous background real-time sync on mobile operating systems.

## Local-only and pre-seeded databases

PowerSync can manage local-only tables without a connector. Use these for device preferences, drafts that must never sync, derived plaintext, or local indexes. Define logout/clear semantics explicitly.

Pre-seeding can reduce first-use latency by shipping a baseline SQLite file, but it must match PowerSync's expected structure/version and still reconcile with checkpoints. Evaluate app-binary size, staleness, per-user privacy, and upgrade compatibility before using it.

## Pagination and large datasets

Run pagination against local SQLite. Prefer stable keyset/cursor pagination for large or changing lists; `LIMIT/OFFSET` is simple but can become slow/unstable. Pair local pagination with on-demand Sync Streams when the full server dataset should not be on device.

Prioritize essential tables, minimize columns, index local filters, observe download progress, and design UX that remains useful with partially synchronized optional data.

Primary documentation: [advanced client topics](https://docs.powersync.com/client-sdks/advanced/attachments), [encryption](https://docs.powersync.com/client-sdks/advanced/data-encryption), [raw tables](https://docs.powersync.com/client-sdks/advanced/raw-tables), [background syncing](https://docs.powersync.com/client-sdks/advanced/background-syncing), [full-text search](https://docs.powersync.com/client-sdks/full-text-search), and [infinite scrolling](https://docs.powersync.com/client-sdks/infinite-scrolling).
