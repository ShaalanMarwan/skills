# Self-hosting PowerSync

## Contents

- Scope and licensing
- CLI-first local setup
- Service configuration
- Minimal and production topology
- Load balancing and scaling
- Deployment targets
- Updating configuration
- Security and operations checklist

## Scope and licensing

PowerSync Service is source-available and distributed as the `journeyapps/powersync-service` container. PowerSync Open Edition can be self-hosted; an Enterprise Self-Hosted Edition adds commercial support/features. Confirm current licensing and image tags before deployment.

The managed Dashboard is not available for a self-hosted instance. Use version-controlled configuration, the PowerSync CLI, diagnostics/admin APIs, and your infrastructure tooling.

## CLI-first local setup

For a new local environment, prefer generated configuration:

```bash
npm install -g powersync
powersync init self-hosted
powersync docker configure --database postgres --storage postgres
powersync validate
powersync docker start
powersync status
```

Do not run `powersync login` for a self-hosted-only service; that command stores a PowerSync Cloud PAT. Self-hosted admin API operations use the configured admin token/environment.

The CLI-generated directory typically contains `service.yaml`, `sync-config.yaml`, `cli.yaml`, and Docker Compose resources. Inspect generated schema/comments rather than reconstructing them from memory. The official `self-host-demo` repository contains working variants for Postgres, MongoDB, MySQL, SQL Server, Convex, Supabase, custom checkpoints, and Postgres bucket storage.

## Service configuration

Configuration can be mounted as YAML/JSON, injected as base64, or passed through a supported command option. Prefer a mounted `service.yaml` plus separate `sync-config.yaml` for version control and review.

Core structure:

```yaml
replication:
  connections:
    - type: postgresql
      uri: !env PS_DATABASE_URI
      sslmode: verify-full

storage:
  type: postgresql
  uri: !env PS_STORAGE_URI
  sslmode: verify-full

port: 8080

sync_config:
  path: sync-config.yaml

client_auth:
  jwks_uri: !env PS_JWKS_URI
  audience:
    - !env PS_JWT_AUDIENCE

api:
  tokens:
    - !env PS_ADMIN_TOKEN

telemetry:
  prometheus_port: 9090
  disable_telemetry_sharing: false

system:
  logging:
    level: info
    format: json
```

Only environment variables beginning with `PS_` are substitutable through `!env`. Use the published service JSON schema/current CLI templates to verify exact keys.

Bucket storage is separate from the source database:

- **MongoDB** requires replica-set mode. One node is acceptable for development; use a resilient replica set for production.
- **Postgres** bucket storage needs a dedicated user/schema. Postgres 14+ may share the same server as the source through separate schemas/databases, but separate servers reduce contention; older versions require separation.

Prefer asymmetric JWKS auth. Never publish admin, source database, bucket storage, or signing secrets to the client.

## Minimal and production topology

Official baseline guidance (review current docs before sizing):

### Minimal development/staging

- one unified API + replication container, roughly 1 vCPU / 512 MB;
- one MongoDB replica-set node (or Postgres bucket storage), sized separately;
- TLS-capable load balancer/reverse proxy;
- no redundancy; storage failure may require rebuilding buckets and client resync.

### Production baseline

- one active replication process, with controlled warm/rolling replacement;
- two or more stateless API containers;
- resilient MongoDB replica set or production Postgres bucket storage;
- redundant TLS load balancer;
- daily compaction job;
- migrations run automatically or as an explicit pre-deploy job;
- monitoring, logs, diagnostics, alerts, and configuration backups.

Use `NODE_OPTIONS=--max-old-space-size-percentage=80` for container-aware V8 heap sizing where recommended.

Split roles with:

```text
start -r sync    # replication
start -r api     # client/admin API
compact          # scheduled compaction
migrate up       # explicit storage migration job
```

Only one replication process can hold the replication lock. A brief lock message during rolling replacement is normal; persistent `PSYNC_S1003` indicates competing replicas.

## Load balancing and scaling

- API containers are stateless and scale horizontally. Current guidance targets about 100 concurrent connections per pod/container and documents a 200 hard cap per API process; confirm the version's limit.
- Scale replication vertically according to source write throughput; adding active replication replicas does not improve throughput because only one owns the lock.
- Put PowerSync on a dedicated HTTPS subdomain.
- Disable reverse-proxy response buffering and support HTTP streaming/WebSockets/HTTP2 with long idle/read/send timeouts.
- Use `/probes/startup` and `/probes/liveness` for orchestration/load balancer probes.
- Scrape each process's Prometheus endpoint separately.
- For capacity beyond one instance, create independent instances with independent bucket storage and deterministically pin each user to one endpoint. Do not randomly load-balance a user across instances; switching forces a full resync.

## Deployment targets

### AWS ECS/Fargate

Use private subnets for tasks, public ALB/NAT as needed, Secrets Manager for config/URIs/JWKS, TLS at ALB, long ALB idle timeouts, and connection-based scaling from Prometheus/CloudWatch metrics. Production uses separate replication and API services.

### AWS EKS/Kubernetes

The community Helm chart packages API, replication, compaction, and migration workloads. Use a dedicated namespace, anti-affinity for replication standby, PDBs, NetworkPolicy, TLS ingress with buffering disabled, Prometheus, and HPA/KEDA based on connection metrics plus CPU fallback.

### Coolify

Use the documented Compose resource with an external source/auth/upload service or Supabase. Replace demonstration tokens/passwords, configure a real replica set/storage, mount service/sync config, add TLS and health checks, and remove public database ports.

### Railway

The starter template demonstrates PowerSync, source Postgres, bucket Postgres, an insecure demo backend, diagnostics, and schema scripts. Treat it as a demo: secure/replace the backend and auth, restrict publications, replace tokens, and use current Sync Streams rather than copying legacy example rules.

## Updating configuration

Three self-hosted sync-config paths exist:

1. CLI: edit `powersync/sync-config.yaml`, `powersync validate`, then apply with the CLI/Docker workflow.
2. Mounted file: update config and restart the Service.
3. Admin API: validate/deploy at runtime with a bearer admin token, unless file-based sync config disables the API path.

PowerSync keeps the active config serving while a new config performs initial replication, then transitions clients. Monitor the deploying config, replication slot/WAL budget, and bucket storage growth.

Service configuration, image, and storage migrations require a controlled infrastructure rollout. If automatic migrations are disabled, the explicit migration job must run before starting an incompatible service version.

## Security and operations checklist

- [ ] TLS from clients to load balancer and from Service to public databases/JWKS.
- [ ] Service/API containers are not directly public; only required ingress is exposed.
- [ ] Source and bucket databases live on private networks or restricted endpoints.
- [ ] Strong secret-manager values replace every demo credential.
- [ ] Admin/diagnostics endpoints require strong tokens and network restrictions.
- [ ] Replication identity has only required CDC/SELECT rights.
- [ ] Sync Streams and backend writes both enforce authorization.
- [ ] Health/startup probes, logs, Prometheus metrics, replication-lag/WAL alerts exist.
- [ ] API connection capacity and bucket storage growth have headroom.
- [ ] Daily compaction and schema/storage migration procedures are scheduled.
- [ ] Service/sync configuration is reviewed and version-controlled; secrets are not.
- [ ] Bucket storage backup/rebuild and client-resync consequences are documented.
- [ ] Telemetry sharing choice is deliberate (`disable_telemetry_sharing`).
- [ ] Rollback compatibility between service image and bucket-storage schema is verified.

Primary documentation: [self-hosting intro](https://docs.powersync.com/intro/self-hosting), [instance configuration](https://docs.powersync.com/configuration/powersync-service/self-hosted-instances), [deployment architecture](https://docs.powersync.com/maintenance-ops/self-hosting/deployment-architecture), [self-host operations](https://docs.powersync.com/maintenance-ops/self-hosting/overview), and [local development](https://docs.powersync.com/tools/local-development).
