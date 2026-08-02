# Schema and modeling

## Tables and columns

Every persistent table should have a stable primary key. Use an auto-increment integer when local ordering and generated IDs fit; use explicit or composite keys when the domain already has stable identity. For offline synchronization, consider client-generated identifiers rather than server-dependent auto-increments.

Available storage families include integers, 64-bit `BigInt`, text, booleans, real numbers, blobs, datetimes, SQLite `ANY` for strict tables, enums, and values mapped through converters. Use `int64()` for integers that may exceed JavaScript's exact numeric range on web.

Columns are non-nullable by default. Distinguish:

- `withDefault`: a database `DEFAULT` constraint and therefore part of the schema;
- `clientDefault`: generated Dart insert behavior, not enforced for external SQL and not a schema change;
- `nullable`: a real database nullability decision;
- `withLength`: legacy Dart-side validation, not a strong database constraint;
- `check`: a database constraint that existing rows must satisfy during migration.

Drift recommends ISO-8601 text datetime storage for new projects because it preserves precision and UTC information better than the backward-compatible Unix-seconds default. Choose once at project start where possible; changing modes requires converting every datetime column plus reviewing custom SQL, views, and triggers.

## Keys, references, and indexes

- Use `unique()` for one column and `uniqueKeys` for composite uniqueness.
- Index columns used frequently in filters or ordering after checking query plans and data size. Primary keys, unique columns, and foreign-key targets already receive indexes.
- Enable SQLite foreign keys with `PRAGMA foreign_keys = ON` on every open, normally in `beforeOpen`.
- Specify `onDelete` and `onUpdate` actions deliberately.
- Use `@ReferenceName` when multiple references would cause generated manager names to collide.
- Treat custom constraints carefully: `customConstraint` replaces Drift's generated constraints, including `NOT NULL`, unless included explicitly.

`STRICT`, `WITHOUT ROWID`, generated columns, partial indexes, views, triggers, and virtual tables are advanced schema tools. Verify target SQLite versions and migration support before using them.

## Rows and companions

Generated row classes represent complete rows. Companions represent partial rows and distinguish absent from present-null with `Value`. Use companions for partial updates and inserts with generated/default values. The manager API hides companions for many common operations.

Custom row classes can use constructors, records, static or asynchronous factories, and generated `toColumns` mixins. Use them when domain inheritance or another serialization builder matters. Drift's built-in JSON serialization is intentionally limited; prefer a dedicated serializer for complex application contracts.

## Type converters and enums

Converters map a Dart type to a supported SQL storage type. Implement value equality on converted Dart objects if generated row equality should be meaningful. Use `equalsValue` or explicit conversion in expressions so comparisons operate on stored values correctly.

Prefer modern `JsonTypeConverter2` variants. SQLite JSONB is useful mainly when SQLite itself processes JSON; textual JSON is more portable and is the general default.

Enum storage has migration hazards:

- integer/index storage breaks when values are inserted or reordered;
- text/name storage breaks when values are renamed;
- neither permits casually applying another converter on the same column.

## Relationship modeling

Drift is relational but is not an identity-map ORM and does not automatically fetch object graphs. Model many-to-many relationships with junction tables for strong relational integrity. JSON arrays may simplify ordered embedded structures but weaken relational constraints and portability. Choose based on update patterns, ordering, integrity, and query requirements—not convenience alone.
