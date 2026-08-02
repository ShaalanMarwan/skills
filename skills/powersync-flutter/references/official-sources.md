# Official sources

Use primary PowerSync, package, database, and Drift sources. Verify version-sensitive behavior against the currently installed SDK and Service image.

## Documentation corpus

- [PowerSync documentation](https://docs.powersync.com/intro/powersync-overview)
- [Documentation index (`llms.txt`)](https://docs.powersync.com/llms.txt)
- [Complete documentation corpus (`llms-full.txt`)](https://docs.powersync.com/llms-full.txt)
- [Setup guide](https://docs.powersync.com/intro/setup-guide)
- [Flutter SDK guide](https://docs.powersync.com/client-sdks/reference/flutter)
- [Flutter API reference](https://docs.powersync.com/client-sdks/reference/flutter-api)
- [Flutter/Drift ORM support](https://docs.powersync.com/client-sdks/orms/flutter-orm-support)
- [Self-hosting](https://docs.powersync.com/intro/self-hosting)
- [Self-host configuration](https://docs.powersync.com/configuration/powersync-service/self-hosted-instances)
- [Self-host operations](https://docs.powersync.com/maintenance-ops/self-hosting/overview)
- [Sync Streams](https://docs.powersync.com/sync/streams/overview)
- [Supported Sync SQL](https://docs.powersync.com/sync/supported-sql)
- [Writes](https://docs.powersync.com/handling-writes/writing-client-changes)
- [Authentication](https://docs.powersync.com/configuration/auth/overview)
- [CLI](https://docs.powersync.com/tools/cli)
- [Debugging](https://docs.powersync.com/debugging/troubleshooting)

## Official repositories

- [PowerSync organization](https://github.com/powersync-ja)
- [Flutter/Dart SDK (`powersync.dart`)](https://github.com/powersync-ja/powersync.dart)
- [PowerSync Service](https://github.com/powersync-ja/powersync-service)
- [PowerSync documentation source](https://github.com/powersync-ja/powersync-docs)
- [PowerSync CLI](https://github.com/powersync-ja/powersync-cli)
- [Self-host demo](https://github.com/powersync-ja/self-host-demo)
- [`sqlite_async.dart` and `drift_sqlite_async`](https://github.com/powersync-ja/sqlite_async.dart)
- [PowerSync SQLite core](https://github.com/powersync-ja/powersync-sqlite-core)
- [Official PowerSync agent skills](https://github.com/powersync-ja/agent-skills)
- [Official PowerSync Flutter + Drift demo](https://github.com/powersync-ja/powersync.dart/tree/main/demos/supabase-todolist-drift)
- [Self-host Kubernetes Helm chart (community)](https://github.com/powersync-community/powersync-helm-chart)

## Packages and releases

- [`powersync` on pub.dev](https://pub.dev/packages/powersync)
- [`drift_sqlite_async` on pub.dev](https://pub.dev/packages/drift_sqlite_async)
- [`sqlite_async` on pub.dev](https://pub.dev/packages/sqlite_async)
- [`drift` on pub.dev](https://pub.dev/packages/drift)
- [PowerSync Flutter releases](https://github.com/powersync-ja/powersync.dart/releases)
- [PowerSync Service container tags](https://hub.docker.com/r/journeyapps/powersync-service/tags)
- [PowerSync release notes](https://releases.powersync.com/)
- [Feature status](https://docs.powersync.com/resources/feature-status)
- [Supported platforms](https://docs.powersync.com/resources/supported-platforms)

## Related primary references

- [Drift documentation](https://drift.simonbinder.eu/)
- [Drift source](https://github.com/simolus3/drift)
- [SQLite documentation](https://sqlite.org/docs.html)
- [Postgres logical replication](https://www.postgresql.org/docs/current/logical-replication.html)
- [MongoDB change streams](https://www.mongodb.com/docs/manual/changeStreams/)
- [MySQL binary log](https://dev.mysql.com/doc/refman/8.4/en/binary-log.html)
- [SQL Server change data capture](https://learn.microsoft.com/en-us/sql/relational-databases/track-changes/about-change-data-capture-sql-server)

## Audit snapshot

This skill was built from the official documentation corpus retrieved on 2026-08-02 and from read-only snapshots of the default branches of `powersync.dart`, `powersync-service`, `self-host-demo`, `sqlite_async.dart`, and `agent-skills`. See [documentation-coverage.md](documentation-coverage.md) for the complete page inventory and coverage counts.
