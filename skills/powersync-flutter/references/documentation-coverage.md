# Documentation coverage

This skill was built from the complete official PowerSync documentation corpus retrieved on 2026-08-02, not only the overview page. The audit compared the official `llms.txt` index with every `Source:` marker in `llms-full.txt`. It accounted for **173 documentation pages, 40,819 source lines, and 213,147 words**. The three optional index links (GitHub, Discord, and the product website) are not documentation pages.

## Coverage by official section

| Section | Pages | Approx. words |
|---|---:|---:|
| Architecture | 5 | 3,798 |
| Client SDKs | 58 | 74,143 |
| Configuration | 18 | 23,738 |
| Debugging | 2 | 5,057 |
| Handling writes | 5 | 7,999 |
| Integrations | 8 | 9,610 |
| Introduction/setup | 5 | 11,386 |
| Maintenance and operations | 21 | 25,371 |
| Migration guides | 1 | 1,628 |
| Resources/security/limits | 11 | 11,424 |
| Sync Streams and legacy rules | 29 | 32,142 |
| Tools | 10 | 6,846 |
| **Total** | **173** | **213,142+** |

The small difference from the full-file word count is index/title text before the first page marker.

## Focused cross-checks

The audit separately cross-checked the Flutter SDK and Drift adapter against the current `powersync.dart` demo and `sqlite_async.dart` adapter implementation. Self-hosting coverage includes the introduction, instance configuration, local CLI/Docker development, and all 14 maintenance/deployment pages: ECS, EKS, Coolify, deployment architecture, diagnostics, health checks, instance migration, monitoring, multiple instances, operations overview, Railway, security, sync-config updates, and usage reporting.

## Complete page inventory

| # | Section | Page |
|---:|---|---|
| 1 | architecture | [Architecture Overview](https://docs.powersync.com/architecture/architecture-overview) |
| 2 | architecture | [Client Architecture](https://docs.powersync.com/architecture/client-architecture) |
| 3 | architecture | [Consistency](https://docs.powersync.com/architecture/consistency) |
| 4 | architecture | [PowerSync Protocol](https://docs.powersync.com/architecture/powersync-protocol) |
| 5 | architecture | [PowerSync Service](https://docs.powersync.com/architecture/powersync-service) |
| 6 | client-sdks | [Attachments / Files](https://docs.powersync.com/client-sdks/advanced/attachments) |
| 7 | client-sdks | [Background Syncing](https://docs.powersync.com/client-sdks/advanced/background-syncing) |
| 8 | client-sdks | [CRDT Data Structures](https://docs.powersync.com/client-sdks/advanced/crdts) |
| 9 | client-sdks | [JSON, Arrays and Custom Types](https://docs.powersync.com/client-sdks/advanced/custom-types-arrays-and-json) |
| 10 | client-sdks | [Data Encryption](https://docs.powersync.com/client-sdks/advanced/data-encryption) |
| 11 | client-sdks | [GIS Data: PostGIS](https://docs.powersync.com/client-sdks/advanced/gis-data-postgis) |
| 12 | client-sdks | [Local-Only Usage](https://docs.powersync.com/client-sdks/advanced/local-only-usage) |
| 13 | client-sdks | [Pre-Seeding SQLite Databases](https://docs.powersync.com/client-sdks/advanced/pre-seeded-sqlite) |
| 14 | client-sdks | [Querying JSON Data in SQLite](https://docs.powersync.com/client-sdks/advanced/query-json-in-sqlite) |
| 15 | client-sdks | [Raw SQLite Tables to Bypass JSON View Limitations](https://docs.powersync.com/client-sdks/advanced/raw-tables) |
| 16 | client-sdks | [Sequential ID Mapping](https://docs.powersync.com/client-sdks/advanced/sequential-id-mapping) |
| 17 | client-sdks | [Using SQLite Extensions](https://docs.powersync.com/client-sdks/advanced/sqlite-extensions) |
| 18 | client-sdks | [State Management Libraries](https://docs.powersync.com/client-sdks/advanced/state-management) |
| 19 | client-sdks | [Unit Testing](https://docs.powersync.com/client-sdks/advanced/unit-testing) |
| 20 | client-sdks | [Cascading Delete](https://docs.powersync.com/client-sdks/cascading-delete) |
| 21 | client-sdks | [Expo Go Support](https://docs.powersync.com/client-sdks/frameworks/expo-go-support) |
| 22 | client-sdks | [Dart/Flutter Web Support (Beta)](https://docs.powersync.com/client-sdks/frameworks/flutter-web-support) |
| 23 | client-sdks | [Next.js + PowerSync](https://docs.powersync.com/client-sdks/frameworks/next-js) |
| 24 | client-sdks | [Nuxt Integration](https://docs.powersync.com/client-sdks/frameworks/nuxt) |
| 25 | client-sdks | [React Hooks](https://docs.powersync.com/client-sdks/frameworks/react) |
| 26 | client-sdks | [React Native Web Support](https://docs.powersync.com/client-sdks/frameworks/react-native-web-support) |
| 27 | client-sdks | [TanStack Query & TanStack DB](https://docs.powersync.com/client-sdks/frameworks/tanstack) |
| 28 | client-sdks | [Vue Composables](https://docs.powersync.com/client-sdks/frameworks/vue) |
| 29 | client-sdks | [Full-Text Search](https://docs.powersync.com/client-sdks/full-text-search) |
| 30 | client-sdks | [Experimental: High Performance Diffs](https://docs.powersync.com/client-sdks/high-performance-diffs) |
| 31 | client-sdks | [Infinite Scrolling](https://docs.powersync.com/client-sdks/infinite-scrolling) |
| 32 | client-sdks | [Dart/Flutter ORM Support](https://docs.powersync.com/client-sdks/orms/flutter-orm-support) |
| 33 | client-sdks | [Drizzle](https://docs.powersync.com/client-sdks/orms/js/drizzle) |
| 34 | client-sdks | [Kysely](https://docs.powersync.com/client-sdks/orms/js/kysely) |
| 35 | client-sdks | [JavaScript ORMs Overview](https://docs.powersync.com/client-sdks/orms/js/overview) |
| 36 | client-sdks | [TanStack DB](https://docs.powersync.com/client-sdks/orms/js/tanstack-db) |
| 37 | client-sdks | [Kotlin SQL Libraries](https://docs.powersync.com/client-sdks/orms/kotlin/overview) |
| 38 | client-sdks | [Room (Beta)](https://docs.powersync.com/client-sdks/orms/kotlin/room) |
| 39 | client-sdks | [SQLDelight (Beta)](https://docs.powersync.com/client-sdks/orms/kotlin/sqldelight) |
| 40 | client-sdks | [ORM Support Overview](https://docs.powersync.com/client-sdks/orms/overview) |
| 41 | client-sdks | [GRDB (Alpha)](https://docs.powersync.com/client-sdks/orms/swift/grdb) |
| 42 | client-sdks | [Client SDKs Overview](https://docs.powersync.com/client-sdks/overview) |
| 43 | client-sdks | [Reading Data](https://docs.powersync.com/client-sdks/reading-data) |
| 44 | client-sdks | [Capacitor SDK (beta)](https://docs.powersync.com/client-sdks/reference/capacitor) |
| 45 | client-sdks | [Capacitor SDK API Reference](https://docs.powersync.com/client-sdks/reference/capacitor-api) |
| 46 | client-sdks | [.NET SDK (beta)](https://docs.powersync.com/client-sdks/reference/dotnet) |
| 47 | client-sdks | [Dart/Flutter SDK](https://docs.powersync.com/client-sdks/reference/flutter) |
| 48 | client-sdks | [Flutter SDK API Reference](https://docs.powersync.com/client-sdks/reference/flutter-api) |
| 49 | client-sdks | [JavaScript Web SDK](https://docs.powersync.com/client-sdks/reference/javascript-web) |
| 50 | client-sdks | [JavaScript Web SDK API Reference](https://docs.powersync.com/client-sdks/reference/javascript-web-api) |
| 51 | client-sdks | [Kotlin SDK](https://docs.powersync.com/client-sdks/reference/kotlin) |
| 52 | client-sdks | [Kotlin SDK API Reference](https://docs.powersync.com/client-sdks/reference/kotlin-api) |
| 53 | client-sdks | [Node.js client SDK (Beta)](https://docs.powersync.com/client-sdks/reference/node) |
| 54 | client-sdks | [Node.js SDK API Reference](https://docs.powersync.com/client-sdks/reference/node-api) |
| 55 | client-sdks | [React Native & Expo SDK](https://docs.powersync.com/client-sdks/reference/react-native-and-expo) |
| 56 | client-sdks | [React Native SDK API Reference](https://docs.powersync.com/client-sdks/reference/react-native-api) |
| 57 | client-sdks | [Rust SDK (alpha)](https://docs.powersync.com/client-sdks/reference/rust) |
| 58 | client-sdks | [Swift SDK](https://docs.powersync.com/client-sdks/reference/swift) |
| 59 | client-sdks | [Swift SDK API Reference](https://docs.powersync.com/client-sdks/reference/swift-api) |
| 60 | client-sdks | [Tauri SDK (alpha)](https://docs.powersync.com/client-sdks/reference/tauri) |
| 61 | client-sdks | [Usage Examples](https://docs.powersync.com/client-sdks/usage-examples) |
| 62 | client-sdks | [Live Queries / Watch Queries](https://docs.powersync.com/client-sdks/watch-queries) |
| 63 | client-sdks | [Writing Data](https://docs.powersync.com/client-sdks/writing-data) |
| 64 | configuration | [Client-Side Integration With Your Backend](https://docs.powersync.com/configuration/app-backend/client-side-integration) |
| 65 | configuration | [CloudCode for MongoDB Backends](https://docs.powersync.com/configuration/app-backend/cloudcode) |
| 66 | configuration | [App Backend Setup](https://docs.powersync.com/configuration/app-backend/setup) |
| 67 | configuration | [Auth0](https://docs.powersync.com/configuration/auth/auth0) |
| 68 | configuration | [Custom Authentication](https://docs.powersync.com/configuration/auth/custom) |
| 69 | configuration | [Development Tokens](https://docs.powersync.com/configuration/auth/development-tokens) |
| 70 | configuration | [Firebase Auth](https://docs.powersync.com/configuration/auth/firebase-auth) |
| 71 | configuration | [Authentication Setup](https://docs.powersync.com/configuration/auth/overview) |
| 72 | configuration | [Supabase Auth](https://docs.powersync.com/configuration/auth/supabase-auth) |
| 73 | configuration | [Stytch + Supabase](https://docs.powersync.com/configuration/auth/supabase-auth/stytch) |
| 74 | configuration | [PowerSync Cloud Instances](https://docs.powersync.com/configuration/powersync-service/cloud-instances) |
| 75 | configuration | [Self-Hosted Instance Configuration](https://docs.powersync.com/configuration/powersync-service/self-hosted-instances) |
| 76 | configuration | [Source Database Connection](https://docs.powersync.com/configuration/source-db/connection) |
| 77 | configuration | [Postgres Maintenance](https://docs.powersync.com/configuration/source-db/postgres-maintenance) |
| 78 | configuration | [Private Endpoints](https://docs.powersync.com/configuration/source-db/private-endpoints) |
| 79 | configuration | [Security & IP Filtering](https://docs.powersync.com/configuration/source-db/security-and-ip-filtering) |
| 80 | configuration | [Source Database Setup](https://docs.powersync.com/configuration/source-db/setup) |
| 81 | configuration | [Advanced SQL Server Configuration](https://docs.powersync.com/configuration/source-db/sql-server-additional-configuration) |
| 82 | debugging | [Error Codes Reference](https://docs.powersync.com/debugging/error-codes) |
| 83 | debugging | [Troubleshooting](https://docs.powersync.com/debugging/troubleshooting) |
| 84 | handling-writes | [Custom Conflict Resolution](https://docs.powersync.com/handling-writes/custom-conflict-resolution) |
| 85 | handling-writes | [Data Pipelines](https://docs.powersync.com/handling-writes/custom-write-checkpoints) |
| 86 | handling-writes | [Handling Update Conflicts](https://docs.powersync.com/handling-writes/handling-update-conflicts) |
| 87 | handling-writes | [Handling Write / Validation Errors](https://docs.powersync.com/handling-writes/handling-write-validation-errors) |
| 88 | handling-writes | [Writing Client Changes](https://docs.powersync.com/handling-writes/writing-client-changes) |
| 89 | integrations | [Neon + PowerSync](https://docs.powersync.com/integrations/neon) |
| 90 | integrations | [Integrations Overview](https://docs.powersync.com/integrations/overview) |
| 91 | integrations | [Serverpod + PowerSync](https://docs.powersync.com/integrations/serverpod) |
| 92 | integrations | [Improve Supabase Connector](https://docs.powersync.com/integrations/supabase/connector-performance) |
| 93 | integrations | [Supabase + PowerSync](https://docs.powersync.com/integrations/supabase/guide) |
| 94 | integrations | [Local Development with Supabase and PowerSync](https://docs.powersync.com/integrations/supabase/local-development) |
| 95 | integrations | [Real-time Streaming](https://docs.powersync.com/integrations/supabase/realtime-streaming) |
| 96 | integrations | [RLS and Sync Streams](https://docs.powersync.com/integrations/supabase/rls-and-sync-streams) |
| 97 | intro | [Demo Apps & Example Projects](https://docs.powersync.com/intro/examples) |
| 98 | intro | [PowerSync Docs](https://docs.powersync.com/intro/powersync-overview) |
| 99 | intro | [PowerSync Philosophy](https://docs.powersync.com/intro/powersync-philosophy) |
| 100 | intro | [Self-Hosting](https://docs.powersync.com/intro/self-hosting) |
| 101 | intro | [PowerSync Setup Guide](https://docs.powersync.com/intro/setup-guide) |
| 102 | maintenance-ops | [Understanding the SQLite Database](https://docs.powersync.com/maintenance-ops/client-database-diagnostics) |
| 103 | maintenance-ops | [Compacting Buckets](https://docs.powersync.com/maintenance-ops/compacting-buckets) |
| 104 | maintenance-ops | [Deploying Schema Changes](https://docs.powersync.com/maintenance-ops/deploying-schema-changes) |
| 105 | maintenance-ops | [Implementing Schema Changes](https://docs.powersync.com/maintenance-ops/implementing-schema-changes) |
| 106 | maintenance-ops | [Monitoring and Alerting](https://docs.powersync.com/maintenance-ops/monitoring-and-alerting) |
| 107 | maintenance-ops | [Production Readiness Best Practices Guide](https://docs.powersync.com/maintenance-ops/production-readiness-guide) |
| 108 | maintenance-ops | [Replication Lag](https://docs.powersync.com/maintenance-ops/replication-lag) |
| 109 | maintenance-ops | [Deploy PowerSync on AWS ECS](https://docs.powersync.com/maintenance-ops/self-hosting/aws-ecs) |
| 110 | maintenance-ops | [Deploy PowerSync on AWS EKS](https://docs.powersync.com/maintenance-ops/self-hosting/aws-eks) |
| 111 | maintenance-ops | [Deploy PowerSync Service on Coolify](https://docs.powersync.com/maintenance-ops/self-hosting/coolify) |
| 112 | maintenance-ops | [Deployment Architecture](https://docs.powersync.com/maintenance-ops/self-hosting/deployment-architecture) |
| 113 | maintenance-ops | [Diagnostics](https://docs.powersync.com/maintenance-ops/self-hosting/diagnostics) |
| 114 | maintenance-ops | [Health Checks](https://docs.powersync.com/maintenance-ops/self-hosting/healthchecks) |
| 115 | maintenance-ops | [Migrating Between Instances](https://docs.powersync.com/maintenance-ops/self-hosting/migrating-instances) |
| 116 | maintenance-ops | [Monitoring](https://docs.powersync.com/maintenance-ops/self-hosting/monitoring) |
| 117 | maintenance-ops | [Multiple PowerSync Instances](https://docs.powersync.com/maintenance-ops/self-hosting/multiple-instances) |
| 118 | maintenance-ops | [Self-Hosting Maintenance & Ops](https://docs.powersync.com/maintenance-ops/self-hosting/overview) |
| 119 | maintenance-ops | [Railway + PowerSync](https://docs.powersync.com/maintenance-ops/self-hosting/railway) |
| 120 | maintenance-ops | [Securing Your Deployment](https://docs.powersync.com/maintenance-ops/self-hosting/securing-your-deployment) |
| 121 | maintenance-ops | [Update Sync Streams (Sync Config)](https://docs.powersync.com/maintenance-ops/self-hosting/update-sync-rules) |
| 122 | maintenance-ops | [Usage Reporting](https://docs.powersync.com/maintenance-ops/self-hosting/usage-reporting) |
| 123 | migration-guides | [MongoDB Atlas Device Sync Migration Guide](https://docs.powersync.com/migration-guides/atlas-device-sync) |
| 124 | resources | [Contact Us](https://docs.powersync.com/resources/contact-us) |
| 125 | resources | [FAQ](https://docs.powersync.com/resources/faq) |
| 126 | resources | [Feature Status](https://docs.powersync.com/resources/feature-status) |
| 127 | resources | [HIPAA Compliance](https://docs.powersync.com/resources/hipaa) |
| 128 | resources | [Local-First Software](https://docs.powersync.com/resources/local-first-software) |
| 129 | resources | [Performance and Limits](https://docs.powersync.com/resources/performance-and-limits) |
| 130 | resources | [Security & HIPAA](https://docs.powersync.com/resources/security) |
| 131 | resources | [Supported Platforms](https://docs.powersync.com/resources/supported-platforms) |
| 132 | resources | [Usage & Billing](https://docs.powersync.com/resources/usage-and-billing) |
| 133 | resources | [Pricing Example](https://docs.powersync.com/resources/usage-and-billing/pricing-example) |
| 134 | resources | [FAQ & Troubleshooting](https://docs.powersync.com/resources/usage-and-billing/usage-and-billing-faq) |
| 135 | sync | [Case Sensitivity](https://docs.powersync.com/sync/advanced/case-sensitivity) |
| 136 | sync | [Client ID](https://docs.powersync.com/sync/advanced/client-id) |
| 137 | sync | [Compatibility](https://docs.powersync.com/sync/advanced/compatibility) |
| 138 | sync | [Multiple Client Versions](https://docs.powersync.com/sync/advanced/multiple-client-versions) |
| 139 | sync | [Advanced Topics](https://docs.powersync.com/sync/advanced/overview) |
| 140 | sync | [Partitioned Tables (Postgres)](https://docs.powersync.com/sync/advanced/partitioned-tables) |
| 141 | sync | [Prioritized Sync](https://docs.powersync.com/sync/advanced/prioritized-sync) |
| 142 | sync | [Schemas and Connections](https://docs.powersync.com/sync/advanced/schemas-and-connections) |
| 143 | sync | [Sharded Databases](https://docs.powersync.com/sync/advanced/sharded-databases) |
| 144 | sync | [Sync Data by Time with Sync Streams](https://docs.powersync.com/sync/advanced/sync-data-by-time) |
| 145 | sync | [Grammar Reference (Sync Rules)](https://docs.powersync.com/sync/grammar/sync-rules/index) |
| 146 | sync | [Grammar Reference (Sync Streams)](https://docs.powersync.com/sync/grammar/sync-streams/index) |
| 147 | sync | [Sync Streams and Sync Rules](https://docs.powersync.com/sync/overview) |
| 148 | sync | [Client Parameters](https://docs.powersync.com/sync/rules/client-parameters) |
| 149 | sync | [Data Queries](https://docs.powersync.com/sync/rules/data-queries) |
| 150 | sync | [Global Buckets](https://docs.powersync.com/sync/rules/global-buckets) |
| 151 | sync | [Many-to-Many Relationships and Join Tables in Sync Rules](https://docs.powersync.com/sync/rules/many-to-many-join-tables) |
| 152 | sync | [Organize Data Into Buckets](https://docs.powersync.com/sync/rules/organize-data-into-buckets) |
| 153 | sync | [Sync Rules (Legacy)](https://docs.powersync.com/sync/rules/overview) |
| 154 | sync | [Parameter Queries](https://docs.powersync.com/sync/rules/parameter-queries) |
| 155 | sync | [Client-Side Usage](https://docs.powersync.com/sync/streams/client-usage) |
| 156 | sync | [Common Table Expressions (CTEs)](https://docs.powersync.com/sync/streams/ctes) |
| 157 | sync | [Examples, Patterns & Demos](https://docs.powersync.com/sync/streams/examples) |
| 158 | sync | [Migrating from Sync Rules](https://docs.powersync.com/sync/streams/migration) |
| 159 | sync | [Sync Streams](https://docs.powersync.com/sync/streams/overview) |
| 160 | sync | [Using Parameters](https://docs.powersync.com/sync/streams/parameters) |
| 161 | sync | [Writing Queries](https://docs.powersync.com/sync/streams/queries) |
| 162 | sync | [Supported SQL](https://docs.powersync.com/sync/supported-sql) |
| 163 | sync | [Types](https://docs.powersync.com/sync/types) |
| 164 | tools | [AI Tools](https://docs.powersync.com/tools/ai-tools) |
| 165 | tools | [CLI](https://docs.powersync.com/tools/cli) |
| 166 | tools | [Dart & Flutter DevTools Extension](https://docs.powersync.com/tools/dart-devtools-extension) |
| 167 | tools | [DevTools Integrations](https://docs.powersync.com/tools/devtools-overview) |
| 168 | tools | [Sync Diagnostics Client](https://docs.powersync.com/tools/diagnostics-client) |
| 169 | tools | [Run PowerSync Locally with Docker and the CLI](https://docs.powersync.com/tools/local-development) |
| 170 | tools | [Nuxt DevTools Integration](https://docs.powersync.com/tools/nuxt-inspector) |
| 171 | tools | [Tools](https://docs.powersync.com/tools/overview) |
| 172 | tools | [PowerSync Dashboard](https://docs.powersync.com/tools/powersync-dashboard) |
| 173 | tools | [Terraform Provider](https://docs.powersync.com/tools/terraform) |
