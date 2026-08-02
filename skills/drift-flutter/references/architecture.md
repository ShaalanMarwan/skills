# Architecture and API choices

## Contents

- Mental model
- Schema definition styles
- Generated model
- Query and write choices
- Application boundaries
- Review checklist

## Mental model

Drift is a reactive persistence layer backed by database engines such as SQLite. Its generator analyzes table declarations and SQL at build time, then produces typed rows, companions, table accessors, and query methods. Runtime executors open the actual database. Keep those two concerns separate: generator settings describe what Drift may analyze, while executor configuration determines what the deployed database can actually execute.

## Schema definition styles

### Dart tables

Use classes extending `Table`. This is a strong default for Flutter teams preferring refactorable Dart syntax. Declare keys and constraints close to columns and include each table in `@DriftDatabase`.

### Verified SQL

Use `.drift` files for `CREATE TABLE`, named queries, views, triggers, and indexes when SQL is more expressive. Drift parses and validates SQL during generation, generates typed methods, and supports reactive query results. Add files through the database annotation's `include` set.

Both styles are first-class and can coexist, but avoid mixing styles without a clear module boundary.

## Generated model

- A table produces a row data class representing a complete stored row.
- A companion represents values supplied to inserts and partial updates; `Value.absent()` differs from a present nullable value.
- The generated database superclass exposes typed table and query accessors.
- Generated source is output, not the source of truth. Modify declarations, regenerate, and review the generated diff.

Use explicit SQL names for long-lived schemas when Dart refactors should not rename on-disk objects. Remember that renaming a Dart getter can become a schema change depending on configuration and overrides.

## Query and write choices

- Use `get()`/single-result variants for one-time reads and `watch()`/single-result variants for reactive reads.
- Use the manager API for concise relationship-aware CRUD when it improves readability.
- Use the fluent query API for dynamic filters, joins, ordering, grouping, and composition.
- Use named verified SQL for complex, stable queries whose intent is clearest as SQL.
- Use a transaction when multiple operations must succeed or fail together.
- Use a batch to reduce overhead for many independent statements.
- Use upserts only with a clearly identified conflict target and desired merge semantics.

Reactive invalidation is based on tables read and written. For custom statements, ensure Drift knows which tables a query reads or updates when automatic inference is insufficient.

## Application boundaries

Keep one owned database lifecycle, usually registered through the app's dependency-injection mechanism. Place domain-oriented operations in DAOs or repositories. Map generated database rows into domain models when persistence representation and business representation have different lifecycles.

Avoid querying from widgets directly in large applications. A UI may consume streams, but database ownership, error handling, and transactions belong below the presentation layer.

## Review checklist

- Are primary keys stable and suitable for offline creation if needed?
- Are foreign-key actions explicit and enabled at runtime where required?
- Are uniqueness, checks, and indexes aligned with real invariants and query patterns?
- Are nullable fields truly optional, and are defaults valid for old and new rows?
- Are dates, booleans, enums, JSON, and custom types stored consistently across platforms?
- Are all multi-statement invariants transactional?
- Can the database be constructed with an in-memory executor for tests?
- Are streams subscribed and disposed at the correct architectural layer?
