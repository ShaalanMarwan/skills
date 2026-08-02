# Writes, conflicts, and consistency

## Contents

- Upload queue behavior
- Connector implementation
- Backend contract
- Error classification
- Conflict strategies
- Testing checklist

## Upload queue behavior

Every PowerSync-managed local write is recorded atomically in the blocking FIFO `ps_crud` queue:

| Local SQL | CRUD operation | Payload |
|---|---|---|
| `INSERT` | `PUT` | ID and non-null values |
| `UPDATE` | `PATCH` | ID and changed fields |
| `DELETE` | `DELETE` | ID |

The SDK invokes `uploadData()` after local writes, on connection/reconnection, on periodic keepalives, and after retry delays. It calls the method repeatedly until the queue is empty. If the front operation remains because code returned without completing it, the SDK warns and delays retries to avoid a tight loop.

Uploads occur only while sync is connected. Offline writes remain durable and resume later.

## Connector implementation

Process one transaction or bounded batch per invocation:

```dart
@override
Future<void> uploadData(PowerSyncDatabase database) async {
  final tx = await database.getNextCrudTransaction();
  if (tx == null) return;

  try {
    await api.applyTransaction(
      tx.crud.map((entry) => {
        'client_id': entry.clientId,
        'transaction_id': entry.transactionId,
        'op': entry.op.name,
        'table': entry.table,
        'id': entry.id,
        'data': entry.opData,
        'metadata': entry.metadata,
      }).toList(),
    );
    await tx.complete();
  } on RetryableUploadException {
    rethrow;
  }
}
```

For high-volume independent operations, use a CRUD batch only when the backend contract matches its semantics. Preserve local transaction grouping when atomicity matters.

## Backend contract

The backend endpoint must:

1. Authenticate the application session independently of trusting the supplied operation.
2. Authorize every table/row/field mutation against current server state.
3. Validate table names through an allowlist; never interpolate arbitrary client table/column strings into SQL.
4. Apply each accepted PowerSync transaction synchronously to the source database.
5. Be idempotent because delivery can repeat. Deduplicate with client/operation identity or use naturally idempotent upsert/delete behavior.
6. Return only after the source commit is durable and visible to the database's CDC path.
7. Return a handled success for deliberate validation rejection/conflict if the queue should advance.

Do not enqueue the write for later and acknowledge it immediately. Write checkpoints assume accepted uploads are already in the source database.

## Error classification

| Outcome | Connector action | Result |
|---|---|---|
| Network timeout, temporary source outage, overload | Throw/retry | Keep operation at queue head |
| Unexpected bug or schema mismatch needing intervention | Throw, alert | Block queue until fixed or recovered |
| Validation rejection intentionally handled | Return success details or record a synced error; complete | Queue advances; server state rolls local optimistic change back |
| Conflict intentionally resolved/recorded | Commit resolution/conflict record; complete | Resolution syncs back |
| Permanently invalid operation moved to durable dead-letter queue | Complete after durable dead-letter commit | Queue advances with operational record |

A generic `4xx` that causes `uploadData()` to throw blocks the queue indefinitely. Reserve that behavior for a condition that must block and will actually be fixed. Acknowledged but rejected mutations disappear during reconciliation because the source database did not adopt them.

## Default and custom conflicts

The usual baseline is delete-wins plus last server-received write per field. Different-field `PATCH` operations can coexist; same-field operations resolve by arrival order. The backend owns these rules.

Choose custom behavior by domain:

- **Sequence/version compare**: strong stale-write detection without clock skew; reject/record when versions differ.
- **Timestamp compare**: simpler, but use server time and understand clock/ordering limitations.
- **Field-level metadata**: merge unrelated fields using per-field versions/timestamps.
- **State machine/business validation**: enforce legal transitions such as pending → shipped.
- **Commutative operations**: represent inventory increments/decrements as domain operations rather than overwriting counts.
- **Conflict table**: retain client and server versions for human resolution in high-stakes workflows.
- **CRDT payloads**: use a CRDT library for collaborative text/data structures; PowerSync transports their persisted state/updates.

Advanced PowerSync schema options can track previous values, custom metadata, and ignore empty updates. Use them only when the backend resolution algorithm consumes that information.

## Validation feedback pattern

A robust asynchronous UX uses a synced table such as `write_issues`:

```text
id, user_id, operation_id, entity_type, entity_id,
code, message, client_payload, server_payload, resolved_at
```

The backend records an issue and acknowledges the mutation. Sync Streams expose only that user's unresolved issues. The app watches the local table and presents recovery actions. This avoids blocking the queue while preserving an auditable explanation.

## Testing checklist

- [ ] Duplicate delivery of the same PUT/PATCH/DELETE is harmless.
- [ ] A transaction commits atomically or remains queued.
- [ ] Offline writes survive app restart and upload after reconnect.
- [ ] Temporary errors retry without losing/reordering operations.
- [ ] Permanent validation does not silently block later writes.
- [ ] Server rejection eventually restores authoritative local state.
- [ ] Delete versus offline update follows the chosen policy.
- [ ] Two clients changing the same field and different fields are deterministic.
- [ ] Authorization is checked at upload time, not inferred from prior sync visibility.
- [ ] Alerts expose stuck queue entries and upload errors.
- [ ] Logout does not upload another user's pending data under a new identity.

Primary documentation: [client/backend integration](https://docs.powersync.com/configuration/app-backend/client-side-integration), [writing client changes](https://docs.powersync.com/handling-writes/writing-client-changes), [write errors](https://docs.powersync.com/handling-writes/handling-write-validation-errors), [update conflicts](https://docs.powersync.com/handling-writes/handling-update-conflicts), and [custom conflict resolution](https://docs.powersync.com/handling-writes/custom-conflict-resolution).
