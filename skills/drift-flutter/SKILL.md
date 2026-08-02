---
name: drift-flutter
description: Design, implement, migrate, test, review, and debug Drift persistence in Flutter and Dart applications. Use for pubspec setup, Dart tables or .drift SQL schemas, reactive queries, DAOs and repositories, drift_dev/build_runner generation, SQLite platform connections, web WASM workers, background isolates, schema versions, migration generation and verification, in-memory database tests, and Drift DevTools diagnostics.
---

# Drift for Flutter

Build maintainable Drift databases while protecting existing user data. Treat schema changes as versioned database changes, not ordinary model edits.

## Start with project discovery

1. Inspect `pubspec.yaml`, `pubspec.lock`, `build.yaml`, database declarations, `.drift` files, generated parts, tests, and target platforms.
2. Identify the database class, executor construction, current `schemaVersion`, schema snapshot directory, migration strategy, and state-management or dependency-injection boundary.
3. Preserve the project's established Dart-table or SQL-file style unless the user asks to change it.
4. Check installed package versions before proposing commands. Do not hardcode versions from this skill.
5. Ask before making an irreversible or lossy migration when the desired data transformation cannot be inferred safely.

Read [architecture.md](references/architecture.md) when choosing project boundaries. Read [schema-and-modeling.md](references/schema-and-modeling.md) when defining tables, rows, converters, constraints, or relationships. Read [queries-and-reactivity.md](references/queries-and-reactivity.md) when implementing selects, writes, managers, SQL files, streams, or transactions. Read [platforms.md](references/platforms.md) when opening a database or targeting web, mobile, desktop, encryption, libSQL, or PostgreSQL. Read [migrations-and-testing.md](references/migrations-and-testing.md) before any schema change. Read [tooling.md](references/tooling.md) for generation, validation, tracing, and debugging. Read [data-lifecycle-and-sync.md](references/data-lifecycle-and-sync.md) for existing databases, backup/restore, or synchronization. Read [documentation-coverage.md](references/documentation-coverage.md) and [official-sources.md](references/official-sources.md) when auditing coverage, freshness, or uncommon features.

## Choose the implementation path

- Prefer `drift` plus `drift_flutter` for a cross-platform Flutter application using SQLite.
- Use Dart table declarations when the codebase favors Dart APIs and straightforward queries.
- Use `.drift` files when SQL is central, queries are complex, or compile-time-verified SQL is clearer.
- Use DAOs or repositories to keep feature code independent from database mechanics. Do not expose generated companions throughout the UI layer without an existing project convention supporting that choice.
- Prefer a constructor accepting `QueryExecutor` or `DatabaseConnection`; add a production/default constructor separately. This keeps the database testable.
- Prefer the current recommended background executor on native platforms. Avoid synchronous SQLite work on Flutter's UI isolate.

## Implement safely

1. Add only the dependencies required by the detected targets and selected executor.
2. Define stable SQL names deliberately. Treat changes to table names, column names, types, constraints, defaults, nullability, keys, and indexes as migration work.
3. Model nullability and defaults explicitly. Prefer `clientDefault` when only Drift inserts need a default; use `withDefault` when the schema itself must enforce it.
4. Define foreign keys, unique constraints, checks, indexes, and delete behavior according to domain invariants. Enable `PRAGMA foreign_keys = ON` on every open when relying on SQLite foreign keys.
5. Use generated type-safe queries for normal operations; use verified SQL for queries that are clearer in SQL.
6. Use transactions for multi-step invariants and batches for repeated writes.
7. Return `Future` for snapshots and `Stream` for state that the UI should observe. Keep stream lifecycle and database closure explicit.
8. Run generation, formatting, static analysis, and focused tests after edits.

## Handle schema changes

1. Inspect every stored schema version and existing migration before editing.
2. Change the schema and increment `schemaVersion` exactly once for the new version.
3. Prefer the configured `drift_dev make-migrations` workflow. Keep generated schema snapshots and step files under version control.
4. Fill in the generated migration step. Explicitly transform or backfill data when adding required columns or changing representations.
5. Test upgrades from every supported historical version, not only creation of a fresh database.
6. Validate the resulting runtime schema against the expected Drift schema.
7. Never use destructive conflict-resolution flags or delete database files to hide a migration failure unless the user explicitly requests disposable-data behavior.

## Verify the result

Run the commands appropriate to the project, generally:

```text
dart run build_runner build
flutter analyze
flutter test
```

Use the project's existing command wrappers when present. For generation conflicts, determine whether the files are stale generated artifacts before considering deletion. Do not blindly use `--delete-conflicting-outputs` in a repository containing user-maintained files at conflicting paths.

Report:

- changed schema and query behavior;
- migration path and data-preservation decisions;
- platforms covered;
- generation, analysis, and test results;
- remaining assumptions or manual deployment requirements, especially web assets and headers.

## Guardrails

- Do not edit generated `.g.dart`, `.drift.dart`, schema-step, or generated migration-test code by hand unless the file explicitly contains an intended hand-written section.
- Do not conflate compile-time analyzer configuration with runtime SQLite capabilities.
- Do not assume web persistence behaves identically in every browser; inspect Drift's selected implementation where persistence is critical.
- Do not hold a database transaction open across network calls or UI interactions.
- Do not create multiple independent database instances for the same file without understanding Drift's isolate and stream-coordination behavior.
- Do not create manager-based N+1 relationship reads when prefetching or a join is appropriate.
- Do not reorder integer-backed enum values or rename text-backed enum values without a data migration.
- Do not assume Drift synchronizes data with a backend; synchronization is an application or third-party concern.
- Do not claim a migration is safe merely because a fresh-database test passes.
