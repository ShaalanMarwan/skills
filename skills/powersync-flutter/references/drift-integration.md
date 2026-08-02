# Drift integration

## Contents

- When to choose the adapter
- Detection
- Required model
- Shared connection
- Schema ownership
- Migrations and notifications
- Common mistakes

## When to choose the adapter

Use `drift_sqlite_async` when the Flutter app already uses Drift or needs generated type-safe queries. PowerSync officially recommends this adapter for Drift users because it:

- delegates Drift selects, writes, and transactions to PowerSync's `sqlite_async` connection;
- shares WAL locks and read concurrency;
- forwards PowerSync/external table-update notifications to Drift watch queries;
- supports nested Drift transactions through savepoints;
- optionally supports Drift-managed migrations.

Do not open the PowerSync file with a separate Drift `NativeDatabase`. Separate connections can produce `SQLITE_BUSY`, inconsistent locking, and missing reactive notifications.

## Detection

Run:

```bash
bash scripts/detect_flutter_stack.sh /path/to/flutter-app
```

Treat any of these as evidence that Drift must be preserved:

- `drift` or `drift_dev` in `pubspec.yaml`/lockfile;
- `package:drift/drift.dart` imports;
- `@DriftDatabase` annotations;
- generated database subclasses;
- `.drift` SQL files.

If `drift_sqlite_async` or `SqliteAsyncDriftConnection` already exists, inspect and reuse it. Never create a second adapter around a different PowerSync instance.

## Required model

PowerSync and Drift describe the same client-visible rows for different purposes:

- **PowerSync schema** controls the SQLite views, storage types, synced indexes, local-only/raw behavior, and upload tracking.
- **Drift schema** generates Dart row types, query builders, relationships, and local query APIs.
- **Sync Streams** control which source rows and transformed columns arrive.

All three must agree on table names, column names, nullability assumptions, and SQLite representation.

Unlike native PowerSync table definitions, Drift tables must declare the `id` column:

```dart
class Todos extends Table {
  @override
  String get tableName => 'todos';

  TextColumn get id => text().clientDefault(() => uuid.v4())();
  TextColumn get listId => text().named('list_id')();
  TextColumn get description => text()();
  BoolColumn get completed => boolean().nullable()();
  DateTimeColumn get createdAt => dateTime().nullable().named('created_at')();
}
```

PowerSync's schema for the same table omits `id` and represents Drift `bool`/`DateTime` through SQLite-compatible integer/text values:

```dart
const schema = Schema([
  Table('todos', [
    Column.text('list_id'),
    Column.text('description'),
    Column.integer('completed'),
    Column.text('created_at'),
  ]),
]);
```

Use client-generated text IDs for offline inserts. `uuid.v4()` is available from PowerSync, or use another stable UUID implementation.

## Shared connection

Wrap the already initialized `PowerSyncDatabase`:

```dart
import 'package:drift/drift.dart';
import 'package:drift_sqlite_async/drift_sqlite_async.dart';

@DriftDatabase(tables: [Todos])
class AppDatabase extends $AppDatabase {
  AppDatabase(PowerSyncDatabase powerSync)
      : super(SqliteAsyncDriftConnection(powerSync));

  @override
  int get schemaVersion => 1;
}
```

For dependency injection where PowerSync initializes asynchronously:

```dart
final connection = DatabaseConnection.delayed(Future(() async {
  final powerSync = await ref.read(powerSyncProvider.future);
  return SqliteAsyncDriftConnection(powerSync);
}));

final drift = AppDatabase(connection);
```

Closing `SqliteAsyncDriftConnection` cancels the notification bridge and closes Drift's executor; it does not own/close the underlying PowerSync connection. Close each owner deliberately and in the correct order.

## Schema ownership

For PowerSync-managed synced views, do not call Drift `createAll()` as though Drift owns those tables. PowerSync instantiates the schema. Drift's `onCreate` may create genuinely local structures such as FTS virtual tables, triggers, or auxiliary tables after the PowerSync database has initialized.

Choose one owner for every physical object:

| Object | Recommended owner |
|---|---|
| Synced JSON-backed views | PowerSync schema |
| Sync visibility and column transforms | Sync Streams |
| Dart mappings and typed queries | Drift |
| PowerSync local-only views | PowerSync schema, mirrored in Drift |
| Raw/local physical tables | Explicit migration owner, often Drift |
| FTS virtual tables/triggers | Explicit Drift migration/helper |

Drift relationships express typed query intent but do not imply that foreign-key enforcement or cascades exist on PowerSync views. Perform cascading local writes explicitly in a transaction, and enforce authoritative integrity in the backend.

## Migrations and notifications

Drift migrations can manage local physical schema through the adapter. PowerSync client-view changes are generally applied by PowerSync's schema mechanism. Coordinate versions so old app builds continue to query columns that still exist while new builds roll out.

The adapter listens to `sqlite_async` update notifications and translates each changed table into Drift `TableUpdate`. If a PowerSync local-only table uses an internal name different from its `viewName`, map it:

```dart
final connection = SqliteAsyncDriftConnection(
  powerSync,
  transformTableUpdates: (notification) {
    return notification.tables.map((name) {
      final driftName = name.startsWith('local_')
          ? name.substring('local_'.length)
          : name;
      return TableUpdate(driftName);
    }).toSet();
  },
);
```

Only add such a transform for actual name mismatches. The adapter may deliver duplicate events; watch queries should tolerate re-execution.

## Common mistakes

- Opening the same database file once through PowerSync and again through a standard Drift executor.
- Letting Drift create PowerSync-managed views/tables.
- Declaring `id` in the PowerSync `Table`, or omitting it from the Drift table.
- Using Dart `DateTime`/`bool` mappings without aligning the underlying text/integer representation.
- Assuming a Drift `.references()` declaration enforces a foreign key on a PowerSync view.
- Keeping both raw PowerSync watch streams and Drift watch streams for the same UI state.
- Forgetting to run Drift code generation after model/query changes.
- Treating local Drift migrations as a substitute for backend schema and Sync Stream rollout planning.
- Missing `transformTableUpdates` when a local-only internal name differs from its view name.

Primary sources: [PowerSync Drift ORM guide](https://docs.powersync.com/client-sdks/orms/flutter-orm-support), [`drift_sqlite_async`](https://github.com/powersync-ja/sqlite_async.dart/tree/main/packages/drift_sqlite_async), and the [official Flutter Drift demo](https://github.com/powersync-ja/powersync.dart/tree/main/demos/supabase-todolist-drift).
