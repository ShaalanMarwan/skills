# Flutter client integration

## Contents

- Packages and setup
- Schema rules
- Database lifecycle
- Backend connector
- Query and write APIs
- Sync Stream subscriptions
- State management
- Web and desktop
- Logout and lifecycle

## Packages and setup

Use current compatible releases and inspect their changelogs before pinning:

```bash
flutter pub add powersync
```

For an existing Drift app also add `drift_sqlite_async`; see [drift-integration.md](drift-integration.md). The native SDK depends on `sqlite_async` internally, and PowerSync 2.x changed package and encryption setup compared with 1.x, so do not copy old imports blindly.

Complete source database, Service, Sync Streams, and auth setup before treating client code as runnable. A client that connects to an undeployed or unauthorized instance will often appear stuck at initial sync.

## Schema rules

Define a PowerSync schema whose table and column names match the rows emitted by Sync Streams:

```dart
import 'package:powersync/powersync.dart';

const schema = Schema([
  Table('todos', [
    Column.text('list_id'),
    Column.text('description'),
    Column.integer('completed'),
    Column.text('created_at'),
  ], indexes: [
    Index('todos_list', [IndexedColumn('list_id')]),
  ]),
]);
```

- Do not include `id` in a native PowerSync `Table`; the SDK supplies it as text.
- Available view storage classes are `text`, `integer`, and `real`. Represent booleans as integer `0/1`; represent timestamps as text (usually ISO 8601) unless the stream deliberately emits an epoch number.
- Index every local predicate/join used in frequent UI queries.
- Define local-only tables explicitly when data must never sync.
- Use raw tables only for SQLite features/performance that views cannot provide; then own DDL, migrations, apply/delete statements, and local-write triggers.

## Database lifecycle

Open one `PowerSyncDatabase` per file and initialize it before use:

```dart
final db = PowerSyncDatabase(
  schema: schema,
  path: databasePath,
  logger: logger,
);

await db.initialize();
```

Then connect when the application has a valid authenticated session:

```dart
db.connect(
  connector: AppConnector(db),
  options: const SyncOptions(
    crudThrottleTime: Duration(milliseconds: 50),
  ),
);
```

`connect()` starts synchronization; it does not mean initial data is ready. Use `waitForFirstSync()`, `statusStream`, `currentStatus`, or per-stream status when a workflow truly needs readiness. Prefer rendering available local data immediately and showing sync state separately.

Close the database when its owning dependency scope is disposed. Avoid a second PowerSync instance for the same path; background engines may reopen the file, but only one active sync connection should be coordinated at a time.

## Backend connector

Implement both authentication and uploads:

```dart
class AppConnector extends PowerSyncBackendConnector {
  AppConnector(this.db);
  final PowerSyncDatabase db;

  @override
  Future<PowerSyncCredentials?> fetchCredentials() async {
    final session = await auth.currentSession();
    if (session == null) return null;

    return PowerSyncCredentials(
      endpoint: await backend.powerSyncEndpoint(),
      token: await backend.freshPowerSyncToken(),
    );
  }

  @override
  Future<void> uploadData(PowerSyncDatabase database) async {
    final transaction = await database.getNextCrudTransaction();
    if (transaction == null) return;

    await backend.applyPowerSyncTransaction(transaction.crud);
    await transaction.complete();
  }
}
```

`fetchCredentials()` must return a fresh token when called. The SDK caches credentials, refreshes near expiry, invalidates on `401`, and retries after offline expiry. A typical JWT lifetime is 5–60 minutes; do not use lifetimes shorter than the SDK's prefetch window.

The SDK automatically loops `uploadData()` until the queue is empty. Process one transaction or bounded batch per call. See the writes reference before implementing error behavior.

## Query and write APIs

```dart
final rows = await db.getAll(
  'SELECT * FROM todos WHERE list_id = ? ORDER BY created_at',
  [listId],
);

final row = await db.getOptional(
  'SELECT * FROM todos WHERE id = ?',
  [todoId],
);

final stream = db.watch(
  'SELECT * FROM todos WHERE list_id = ?',
  parameters: [listId],
);

await db.execute(
  'INSERT INTO todos(id, list_id, description, completed) VALUES(uuid(), ?, ?, 0)',
  [listId, description],
);

await db.writeTransaction((tx) async {
  await tx.execute('DELETE FROM todos WHERE list_id = ?', [listId]);
  await tx.execute('DELETE FROM lists WHERE id = ?', [listId]);
});
```

Use local SQL for sorting, aggregation, pagination, JSON extraction, FTS, and presentation joins. Sync Stream SQL decides row availability; client SQL decides how locally available rows are presented.

## Sync Stream subscriptions

Auto-subscribed streams start with the connection. On-demand streams require an explicit subscription:

```dart
final subscription = await db
    .syncStream('list_todos', {'list_id': listId})
    .subscribe(ttl: const Duration(days: 1));

await subscription.waitForFirstSync();

// Keep the handle for the full feature/screen lifetime.
subscription.unsubscribe();
```

The default cache TTL after unsubscribe is 24 hours. Set a deliberate TTL for sensitive or large data. Generated typed stream wrappers prevent silent mistakes in stream and parameter names; use them when schema generation provides them.

## State management

PowerSync returns `Future` and `Stream`, so provider, Riverpod, BLoC, and `get_it` can own the database without duplicating data:

- Create the database in an async/singleton provider.
- Listen to auth state there and connect/disconnect exactly once.
- Close on provider disposal.
- Expose watched SQL as stream providers.
- Expose `statusStream` separately for UI sync indicators.
- Avoid hydrated/cached copies of rows already persisted in SQLite.

With Drift, expose Drift watch queries instead; external PowerSync changes reach them through the adapter.

## Web and desktop

Flutter Web support is beta and uses SQLite WASM plus workers/OPFS depending on SDK/browser version. Run the current PowerSync web setup command and serve the required WASM/worker assets with correct MIME types, cross-origin policies, and caching. Verify multiple tabs, browser storage persistence, incognito behavior, and deployment headers.

Desktop/mobile paths require a writable application-support location. Do not store the database in temporary/cache directories unless data loss is acceptable.

## Logout and lifecycle

- `disconnect()` stops sync but retains local data.
- `disconnectAndClear()` stops sync and clears server-backed local data; use it for logout/user switch when retained rows could cross accounts.
- Local-only data has separate product semantics; test what should persist after clear/logout.
- On auth token refresh, let the connector return fresh credentials; optionally prefetch when the auth SDK emits a refresh event.
- On background sync, initialize in the background isolate/process, obey platform time limits, avoid concurrent sync connections, upload deliberately, and close resources.

Primary documentation: [Flutter SDK](https://docs.powersync.com/client-sdks/reference/flutter), [reading](https://docs.powersync.com/client-sdks/reading-data), [writing](https://docs.powersync.com/client-sdks/writing-data), [watch queries](https://docs.powersync.com/client-sdks/watch-queries), [usage examples](https://docs.powersync.com/client-sdks/usage-examples), and [supported platforms](https://docs.powersync.com/resources/supported-platforms).
