# Pro Beta: durable HAWM snapshot / CFC run binding

## Finding from live NW-0926 synthetic demonstration, 27 September 2026

Two live user-driven runs returned `SUPPORTED / STOP / control_closure=false` with the same seven failed gates. The API included a `hawm_snapshot_id` in its immediate response, but the persisted `CFCRun` did not. Audit v1 later exported independently selected latest HAWM snapshot and latest CFC run, which could appear related without a recorded link. This is an audit integrity gap; it is **not** an observed frozen CFC controller defect.

## V2 contract

- The optional `cfc_runs.hawm_snapshot_id` column stores the exact immutable HAWM snapshot selected **before** structured execution and included in the saved CFC run. `GET /cfc` and POST `/cfc-from-hawm` expose the persisted value, not a synthetic response-only field.
- A composite foreign key on `(hawm_snapshot_id, conversation_id)` references `(snapshot_id, conversation_id)`, preventing cross-conversation links even if an adapter check is bypassed. The server additionally enforces ownership at the application layer.
- Nullable migration is idempotent; no legacy data is deleted or backfilled. Existing prepared runs, and all pre-migration structured CFC runs, have `hawm_snapshot_id = null`.
- Audit report `HAWM_CFC_AUDIT_REPORT_V2` fetches the latest CFC run **first**, then, when and only when the persisted run has a link, resolves that exact snapshot from the authenticated conversation. The separately listed latest HAWM working state is never silently used as the run's input.
- `binding.status` is one of `BOUND_TO_PERSISTED_SNAPSHOT`, `UNBOUND_LEGACY_RUN`, `UNBOUND_PREPARED_RUN`, `NO_CFC_RUN`. Old runs are explicitly `UNBOUND`: this code cannot certify historical user-visible snapshot IDs retroactively.
- If HAWM state changes during CFC execution or before later export, the run retains the earlier selected snapshot ID. A missing or mismatched bound snapshot fails closed rather than showing the current snapshot as supporting evidence.
- This is an immutable database reference to a **user working state**, not evidence authenticity, a signed retrieval passport, a certification of source independence, or real-world shipment authorization. `DemoSubject` and the frozen controller remain unchanged.

## Acceptance

- New structured run round-trips the snapshot ID through API, service, in-memory and PostgreSQL, and audit.
- Two successive working snapshots or a concurrent edit cannot cause the report to associate a run with the wrong snapshot.
- Legacy runs and prepared fixtures remain explicitly unbound.
- Cross-conversation and nonexistent snapshot references are rejected. Direct SQL bypass is blocked by the composite foreign key.
- Existing database bootstraps twice without deleting legacy NULL runs.
- CFC results, 14-day founding-beta retention, history and unrelated frontend remain unmodified.

## Release sequencing

Do not automatically deploy or merge to Railway's backend branch. Production API uses `pro-beta-v0.1`; frontend uses `main`. Confirm PostgreSQL migration, all API/retention tests and existing data safety before a reviewed API-only release. No browser changes are needed for the durable persisted link.

The Information Passport / CASE 001 project is separately paused pending independent comparison; this PR does not implement provenance receipts.
