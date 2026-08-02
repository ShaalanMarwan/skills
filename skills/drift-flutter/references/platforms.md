# Platform setup

## Contents

- Recommended Flutter connection
- Native mobile and desktop
- Web
- Encryption and alternate backends
- Platform checklist

## Recommended Flutter connection

For ordinary cross-platform Flutter apps, prefer `driftDatabase` from `drift_flutter`. Give the database a stable name and pass native or web options only when needed. Keep the database constructor injectable for tests even when a convenience/default constructor opens production storage.

Choose the application support or documents directory intentionally. Do not silently change the database filename or directory in an update; doing so can look like data loss because the application opens a different file.

## Native mobile and desktop

SQLite calls are synchronous internally. Use Drift's current background-opening API so storage and expensive SQL do not block Flutter's UI isolate. The current documentation recommends `NativeDatabase.createInBackground` for manual native setup and notes that current native Drift supports Dart and Flutter native platforms without the extra SQLite library packages required by older releases.

Use a single database owner for a file. When work must span isolates, use Drift's supported connection/isolate mechanisms instead of opening unrelated executors and expecting reactive streams to coordinate automatically.

Use the optional native read pool only for measured workloads with expensive or startup-heavy reads. It requires WAL to allow concurrent readers with a writer; otherwise lock errors are likely. Transactions and exclusive operations still use the writer connection.

## Web

Flutter web needs matching SQLite WebAssembly and Drift worker assets, conventionally:

```text
web/sqlite3.wasm
web/drift_worker.dart.js
```

Match asset versions to the locked `sqlite3` and `drift` packages. Configure `DriftWebOptions` when using `drift_flutter`, or use `WasmDatabase` for manual control.

Verify after deployment:

- the WASM asset returns `Content-Type: application/wasm`;
- worker and WASM paths resolve beneath the deployed base path;
- caching does not mix incompatible asset and application versions;
- browser feature probing selects an acceptable persistence implementation;
- multiple tabs behave acceptably on supported browsers.

COOP/COEP headers can unlock the preferred shared-memory path:

```text
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

These headers can conflict with popup-based integrations. Test the complete application before enabling them. Drift can fall back to other storage paths when the preferred APIs are unavailable, but fallback performance and multi-tab guarantees may differ.

## Encryption and alternate backends

Treat encrypted SQLite, libSQL, and PostgreSQL as separate design choices. Read the current official platform page before adding packages or executor code. Verify that generator dialect configuration, runtime backend features, migrations, tests, and deployment secrets all agree. Never infer that enabling an analyzer module makes that extension available in the shipped SQLite binary.

- Current native encryption guidance uses SQLite3MultipleCiphers through `sqlite3` build hooks and sets the key in the executor's setup callback. Verify the cipher pragma at runtime. Encrypting an existing plaintext file requires an explicit copy/rekey migration; adding a key pragma is insufficient.
- `drift_libsql` can maintain a synchronized local libSQL replica; `drift_hrana` is remote-only and does not make streams reactive to writes from other clients.
- PostgreSQL generation requires the Postgres dialect. Avoid SQLite-only APIs, prefer Postgres-specific datetime types, and use a dedicated migration system for serious multi-server deployments.

## Platform checklist

- Preserve the database path and name across upgrades.
- Close the database during app or test teardown when ownership ends.
- Verify native background execution.
- Verify web assets, MIME type, headers, storage selection, and multi-tab behavior.
- Test on the oldest supported OS/browser, not only the development machine.
- Confirm runtime SQLite features for FTS, JSON, math, geospatial, or custom functions.
- Preserve or checkpoint associated `-wal`/`-shm` state when importing, exporting, or replacing WAL databases.
