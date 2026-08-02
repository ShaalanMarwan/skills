# Queries and reactivity

## Query surfaces

Choose the clearest surface for each operation:

- manager API for common CRUD, cross-reference filters, ordering, counts, and existence checks;
- Dart query builder for joins, aliases, aggregates, subqueries, compound selects, custom columns, and dynamic composition;
- named `.drift` SQL for complex stable SQL with generated types;
- runtime custom SQL only when compile-time-verified SQL is impractical.

Manager `withReferences` without prefetching can issue one query per result row. Prefetch related data or write a join for collections. Use `@ReferenceName` to resolve generated relation-name clashes.

## Reads and expressions

Use `get`, `getSingle`, and `getSingleOrNull` for snapshots; use matching watch variants for reactive results. Use `readTableOrNull` for nullable sides of outer joins. Aliases are required when the same table participates more than once.

Drift supports filters, boolean algebra, arithmetic, null checks/coalesce, dates, `IN`, aggregates, windows, scalar and full subqueries, JSON functions, select-without-table expressions, and compound set operations. Prefer generated expressions over `CustomExpression`; raw fragments bypass much of Drift's safety.

## Writes and transactions

Updates and deletes without a `where` clause affect every row. Use companions for partial updates, `Companion.custom` for SQL-expression updates, batches for repeated statements, and transactions for multi-step invariants. Upserts need the correct conflict target when uniqueness is not the primary key. Returned row IDs may not identify the updated row in an upsert; use returning APIs when the resulting row matters.

Await every operation started in a transaction. Do not schedule later work that retains the transaction. Streams created outside a transaction refresh only after commit; streams created inside see transactional changes but close when the transaction completes. Nested transactions require executor support.

## Reactive behavior

Streams emit an initial current snapshot. Invalidation is table-based and heuristic: a relevant write may rerun more queries than strictly necessary. External writers do not notify Drift. Runtime custom reads must declare `readsFrom`, and runtime custom writes should declare `updates`, so stream invalidation remains correct.

Keep watched result sets reasonably small and queries efficient. If an external process or independent database instance writes the same file, explicitly notify Drift or use a coordinated remote/isolate connection.

## `.drift` files

`.drift` files support schema DDL, named `SELECT`/`INSERT`/`UPDATE`/`DELETE`, positional and named variables, expandable `IN ?` arrays, imports, verified extensions, and generated typed methods. Newer syntax can express Drift constructs in SQL comments for better generic editor compatibility.

Use `table.**` for structured nested results. Use `LIST(subquery)` cautiously: Drift may execute the inner query once per outer row, producing N+1 behavior. Dart placeholders allow runtime expressions, ordering, limits, and insertables inside verified SQL. Existing row classes and converters can be attached when their fields and types match.

SQLite JSON1 is available through an extra Dart import and analyzer configuration. FTS5 and Geopoly virtual tables are defined in SQL. Analyzer modules only permit static analysis; separately confirm that the deployed SQLite build provides the extension.
