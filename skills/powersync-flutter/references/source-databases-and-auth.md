# Source databases, backends, and authentication

## Contents

- Readiness model
- Source database preparation
- App backend
- JWT authentication
- Supabase
- Security boundaries

## Readiness model

Before client integration, verify:

1. A PowerSync Service instance exists and its endpoint is known.
2. The source database is reachable with the required CDC and read permissions.
3. Required tables/collections participate in publication/change capture.
4. Sync Streams validate, deploy, and complete initial replication.
5. Client JWT verification and audience are configured.
6. A representative user token receives exactly the expected rows.
7. A synchronous, idempotent write path exists if the app is bidirectional.

## Source database preparation

Use a dedicated least-privilege replication account and TLS for non-private networks. Restrict publications/CDC to relevant tables where practical; the Service must process all changes included in the replication feed even when streams do not output them.

| Source | CDC/read requirements | Important operations concern |
|---|---|---|
| Postgres 11+ | Logical replication, replication role, `SELECT`, publication named `powersync` | Monitor replication slots, retained WAL, `max_slot_wal_keep_size`; role often needs `BYPASSRLS` or explicit policies |
| MongoDB 6+ | Change streams; replica set/sharded cluster; read plus checkpoint collection permissions | Pre/post images improve update handling; bucket storage is a separate database concern |
| MySQL 5.7+ (beta) | Row-format binlog, GTID, server ID, replication and `SELECT` privileges | Validate provider binlog retention and beta limitations |
| SQL Server 2019+/Azure SQL (beta) | Change Data Capture and required database permissions | Follow source-specific agent/service configuration |
| Convex (experimental) | Checkpoint table/mutation and deploy key | `uploadData()` can call Convex mutations directly |

For Postgres, inspect inactive/lost slots and WAL lag regularly. Deploying a new sync config can temporarily require an additional replication slot while its initial snapshot processes.

Bucket storage is not the source database. Self-hosted PowerSync separately requires MongoDB or Postgres storage for bucket operation history and metadata.

## App backend

The backend owns client-to-server writes and possibly token generation. It may expose REST, GraphQL, gRPC, server functions, Supabase PostgREST/Edge Functions, or Convex mutations. Regardless of transport it must:

- authenticate the caller;
- authorize current access and validate domain rules;
- use table/operation allowlists;
- apply writes synchronously and idempotently;
- return handled validation outcomes without accidentally blocking the queue;
- expose/obtain fresh PowerSync JWTs when the auth provider's token cannot be verified directly.

PowerSync Service should receive no source-database credentials from a Flutter client. The client receives only its PowerSync endpoint and user JWT.

## JWT authentication

PowerSync verifies bearer JWTs. A usable token has:

- `sub`: text user identity, exposed as `auth.user_id()`;
- `aud`: one of the configured audiences;
- `exp`: a sensible expiration;
- a supported signature whose public key/secret is configured;
- optional claims used by `auth.parameter(...)`.

Prefer asymmetric signing (RS256, EdDSA, or ECDSA) with a JWKS endpoint. It separates signing and verification keys and enables rotation. Use HS256 only when its shared-secret operational risk is understood.

Custom auth flow:

1. App authenticates with its normal provider/backend.
2. Backend issues a short-lived PowerSync-compatible JWT.
3. `fetchCredentials()` returns it with the correct Service endpoint.
4. PowerSync verifies signature, audience, expiry, and claims.
5. Sync Streams use signed claims for visibility.

Development tokens are temporary test tools, not production auth. A self-hosted deployment still needs a real verification key/config; there is no magic unauthenticated `dev: true` client auth mode.

## Supabase

Supabase provides Postgres, auth, and a convenient write API, but the same boundaries remain:

- Create a PowerSync replication role/publication and configure logical replication.
- PowerSync's replication role bypasses or independently handles RLS for the read feed; enforce client visibility in Sync Streams.
- Supabase RLS/PostgREST can enforce upload writes, but test PUT/PATCH/DELETE behavior and transaction needs.
- For multi-operation atomic writes, prefer a database function or Edge Function over separate PostgREST calls.

Supabase supports new asymmetric signing keys and legacy HS256 secrets. Prefer the new keys. For standard hosted connections, PowerSync can often detect the project and configure its JWKS URI/audience. For local or self-hosted Supabase, set explicit JWKS URI and the `authenticated` audience. Missing audience commonly produces `PSYNC_S2105`; wrong/incomplete key rotation produces key lookup/signature errors.

When a user signs out, clear or deliberately preserve local data before another Supabase session connects. Do not reuse pending uploads under a different user.

## Security boundaries

- **Sync Streams are read authorization**, not write authorization.
- **Backend checks are write authorization**, even if the row previously synced.
- **JWT claims are trusted only after verification**; subscription/connection parameters are not trusted.
- **Local encryption protects the device file**, not a compromised authenticated app process.
- **TLS protects transport**; self-hosted reverse proxies must preserve long-lived streaming connections.
- Store service/database/admin secrets in environment/secret managers, never in Flutter assets or source.
- Restrict diagnostic/admin endpoints with strong tokens and network policy.

Primary documentation: [source setup](https://docs.powersync.com/configuration/source-db/setup), [source connection](https://docs.powersync.com/configuration/source-db/connection), [authentication](https://docs.powersync.com/configuration/auth/overview), [custom auth](https://docs.powersync.com/configuration/auth/custom), [Supabase auth](https://docs.powersync.com/configuration/auth/supabase-auth), and [backend setup](https://docs.powersync.com/configuration/app-backend/setup).
