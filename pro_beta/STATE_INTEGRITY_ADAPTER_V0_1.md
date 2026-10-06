# Pro Beta State Integrity Adapter v0.1

Date: 2026-10-06
Status: IMPLEMENTATION CANDIDATE — READ-ONLY

Purpose: connect STATE_INTEGRITY_V0_1 to persisted Pro Beta HAWM state without accepting client-supplied identity claims.

Endpoint: GET /api/conversations/{conversation_id}/state-integrity

Observed state comes from the latest persisted HAWM snapshot, its owning conversation, the actual previous persisted snapshot and the current persisted payload.

Expected identity comes only from the separately persisted HAWMSnapshotIdentity receipt created when the snapshot was saved. The request cannot supply fingerprint, predecessor, lineage, case ID, arm ID or current snapshot ID.

STATE_VALID means only that represented host state matches its registered identity/lineage contract. It does not establish evidence truth, evidence applicability, source independence, CFC closure or execution permission. Every result preserves DOES_NOT_AUTHORIZE_CLOSURE.

Historical snapshots without a receipt return STATE_UNRESOLVED / SNAPSHOT_IDENTITY_NOT_REGISTERED. No historical receipt is reconstructed or backfilled.

Promotion requires full Pro Beta CI, authenticated ownership, production deployment of the read-only endpoint, valid exact-current acceptance, controlled fingerprint mismatch acceptance, no-receipt unresolved acceptance, no frozen CFC changes, and a separate production verification receipt.
