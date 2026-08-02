# Documentation coverage audit

Audit basis: the 50 Markdown source pages under `docs/content` in the official `simolus3/drift` `develop` branch, reviewed on 2026-08-02. The generated website has no working sitemap, so repository content is the authoritative inventory. Generated API reference pages are linked as needed but are not duplicated into this skill.

## Core and setup — reviewed

- `index.md`
- `setup.md`
- `faq.md`

## Dart API — reviewed

- `dart_api/tables.md`
- `dart_api/select.md`
- `dart_api/writes.md`
- `dart_api/expressions.md`
- `dart_api/streams.md`
- `dart_api/schema_inspection.md`
- `dart_api/views.md`
- `dart_api/daos.md`
- `dart_api/manager.md`
- `dart_api/transactions.md`
- `dart_api/rows.md`

## SQL API and converters — reviewed

- `sql_api/index.md`
- `sql_api/drift_files.md`
- `sql_api/extensions.md`
- `sql_api/custom_queries.md`
- `sql_api/sql_ide.md` — explicitly marked outdated/unavailable
- `sql_api/types.md`
- `type_converters.md`

## Migrations — reviewed

- `migrations/index.md`
- `migrations/api.md`
- `migrations/tests.md`
- `migrations/step_by_step.md`
- `migrations/exports.md`

## Platforms and execution — reviewed

- `platforms/index.md`
- `platforms/vm.md`
- `platforms/web.md`
- `platforms/encryption.md`
- `platforms/libsql.md`
- `platforms/postgres.md`
- `isolates.md`
- `testing.md`

## Generation and tools — reviewed

- `generation_options/index.md`
- `generation_options/modular.md`
- `generation_options/in_other_builders.md`
- `tools/index.md`
- `tools/devtools.md`
- `community_tools.md`

## Guides — reviewed

- `guides/datetime-migrations.md`
- `guides/install_from_gh.md`
- `guides/migrating_to_drift.md`
- `guides/upgrading.md`

## Examples — reviewed

- `examples/index.md`
- `examples/flutter.md`
- `examples/existing_databases.md`
- `examples/relationships.md`
- `examples/server_sync.md`
- `examples/tracing.md`

## Plugin mapping

- Core project workflow: `SKILL.md`, `architecture.md`
- Tables, rows, constraints, converters, relationships: `schema-and-modeling.md`
- Query builder, manager, SQL files, writes, transactions, streams: `queries-and-reactivity.md`
- Native, web, isolates, encryption, libSQL, PostgreSQL: `platforms.md`
- Migration APIs, schema exports, verification, unit tests: `migrations-and-testing.md`
- Builders, CLI, DevTools, tracing: `tooling.md`
- Existing databases, backup/restore, sync: `data-lifecycle-and-sync.md`
- Freshness links: `official-sources.md`
