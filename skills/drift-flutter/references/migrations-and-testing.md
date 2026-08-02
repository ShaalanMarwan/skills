# Migrations and testing

## Contents

- Migration invariants
- Guided migration workflow
- Data transformations
- Database tests
- Migration tests
- Failure patterns

## Migration invariants

An installed database is durable user state. A schema declaration describes the newest desired schema; it does not update older files by itself. Each released schema version needs a tested path to the current version.

Keep these artifacts together in version control:

- database declaration and `schemaVersion`;
- migration strategy or generated step application;
- exported JSON schema snapshots;
- generated schema-version helpers;
- migration tests and data-integrity assertions.

## Guided migration workflow

Configure database paths under the `drift_dev` builder in `build.yaml`, then establish the initial snapshot before changing the schema:

```text
dart run drift_dev make-migrations
```

For a new version:

1. Inspect the latest snapshot and migration code.
2. Modify schema declarations.
3. Increment `schemaVersion` once.
4. Run `dart run drift_dev make-migrations` again.
5. Implement the generated step in the intended hand-written location.
6. Add data-preservation assertions to generated migration test scaffolding.
7. Run all migration and database tests.

For complex SQLite migrations, disable foreign keys before the migration when required, run schema work transactionally, perform `PRAGMA foreign_key_check`, and re-enable foreign keys in `beforeOpen`. Pragmas such as `foreign_keys` cannot be changed inside a transaction.

For a project using the lower-level schema flow, dump each version with:

```text
dart run drift_dev schema dump lib/path/to/database.dart drift_schemas/
```

Use `schema steps` and schema-generated tests only when that is the repository's established workflow. Prefer `make-migrations` for a new setup because it coordinates snapshots, steps, and tests.

## Data transformations

- Adding a required column usually needs a database default, a temporary nullable state, or an explicit backfill before enforcing `NOT NULL`.
- Renaming must preserve data through the supported table/column migration API or a copy strategy; dropping and recreating is not a rename.
- Changing representations requires an explicit conversion with invalid-value handling.
- Adding uniqueness requires deciding how to resolve existing duplicates.
- Adding foreign keys requires deciding how to handle orphans.
- Large backfills may need staged or batched execution and realistic timing tests.
- Views, triggers, and indexes whose definitions change generally need to be dropped and recreated; consider `recreateAllViews` where table changes indirectly alter view SQL.

Keep migration SQL deterministic and local. Do not call remote services while a migration transaction is open.

## Database tests

Construct the database with `NativeDatabase.memory()` through an injectable executor. Create a fresh database in `setUp` and close it in `tearDown`. For Flutter widget tests, wrap the executor in `DatabaseConnection` with `closeStreamsSynchronously: true` when open stream cleanup would otherwise leave pending asynchronous work.

Test:

- constraints and defaults;
- inserts, partial updates, deletes, and upserts;
- joins and custom SQL edge cases;
- transaction rollback;
- stream initial values and invalidation after relevant writes;
- type-converter round trips and nullable values;
- repository mapping and error behavior;
- deterministic database time when code depends on SQLite `CURRENT_TIMESTAMP` or `datetime('now')`; mocking Dart's clock alone does not change SQLite's clock.

Assert failed writes as asynchronous operations (for example, pass the returned future to `expectLater(..., throwsA(...))`). Do not wrap a future-returning insert in a synchronous closure and accidentally let the test finish before the database error arrives.

## Migration tests

Test each supported old version to the newest version. Seed meaningful old-version rows before upgrading, then assert both:

1. the resulting schema matches the newest expected schema;
2. preserved and transformed data has the intended values.

A fresh-database test proves only `onCreate`; it does not prove upgrades. Include cases with nulls, duplicates, orphan candidates, legacy enum values, and boundary dates when relevant.

## Failure patterns

- `no such column/table`: missing or incomplete migration, wrong database file, or stale generation.
- schema validation mismatch: manual database change, migration that produces different SQL details, or changed declaration without a versioned migration.
- generator cannot export schema: schema-time constants depend on Flutter-only libraries; move schema-evaluated values into pure Dart code.
- tests hang or report pending timers: unclosed database/stream or missing synchronous stream close option in widget tests.
- works on fresh install but not upgrade: only creation was tested.
