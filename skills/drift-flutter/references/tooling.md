# Tooling and diagnostics

## Contents

- Dependency and generation flow
- Build configuration
- DevTools
- Troubleshooting sequence

## Dependency and generation flow

For a Flutter SQLite project, the usual package roles are:

- `drift`: runtime APIs and generated-code contracts;
- `drift_flutter`: cross-platform Flutter database opening;
- `drift_dev`: compile-time analysis and generation;
- `build_runner`: orchestrates code generation.

Additional packages depend on selected platforms and customization. Read current package constraints rather than copying version numbers from an old example.

Run a one-off build with:

```text
dart run build_runner build
```

Use `dart run build_runner watch` during an active development session. Generated output should be reproducible from declared inputs.

Use the experimental Drift CLI deliberately:

```text
dart run drift_dev analyze
dart run drift_dev identify-databases
dart run drift_dev schema export lib/path/to/database.dart
```

`analyze` checks `.drift` files, `identify-databases` verifies discovery, and `schema export` prints effective `CREATE` statements. Do not confuse `schema export` with versioned JSON snapshots from `schema dump`.

## Build configuration

Use `build.yaml` only for a concrete requirement. Defaults are generally preferred. Important categories include:

- registered databases for `make-migrations`;
- schema and generated-test directories;
- SQL dialect and analyzed SQLite version;
- statically assumed extensions and known functions/tables;
- naming and JSON serialization choices;
- modular generation for large or multi-builder projects;
- `fatal_warnings` in projects that want generator warnings to fail builds.

Analyzer options affect static checking, not the SQLite runtime. Verify both sides when enabling FTS5, JSON, math, RTree, Geopoly, or custom functions.

## DevTools

Drift contributes a Flutter/Dart DevTools extension. Enable the Drift extension in DevTools, then use it to inspect open databases and tables, edit data during development, clear disposable databases, and validate the actual schema against Drift's expected schema.

Use schema validation when debugging upgrade-only issues or unexplained query failures. Do not use manual DevTools edits as the production migration strategy.

The old experimental `.drift` analyzer/IDE plugin page is currently marked outdated and unavailable. Do not recommend enabling it as though it were maintained. Rely on build-time Drift analysis and current editor support.

Use `logStatements` for basic SQL logging and `QueryInterceptor` for scoped tracing, timing, retries, or observability. Avoid recording bind values containing credentials or personal data, and do not add automatic retries around non-idempotent writes without transaction-aware semantics.

## Troubleshooting sequence

1. Reproduce with the smallest failing query or migration test.
2. Check `pubspec.lock`, database path/name, `schemaVersion`, generated timestamps/diffs, and executor selection.
3. Regenerate and read the first Drift/build error, not only cascading analyzer errors.
4. Inspect SQL logging or a query interceptor when runtime statement details matter; avoid logging secrets or sensitive row data.
5. Validate the runtime schema in Drift DevTools or migration-test utilities.
6. Compare failing upgraded data with a fresh database to isolate migration problems.
7. On web, inspect network responses for the WASM and worker, browser console output, selected storage implementation, MIME type, and security headers.
8. Close every database and stream in tests, then rerun a focused test before the full suite.
