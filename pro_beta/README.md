# CFC + HAWM Pro Beta v0.1

This branch starts the commercial Pro Beta work without modifying the frozen CFC controller.

## Commercial target

Initial individual plan: **£10/month**.

The first Pro Beta should prove that users value saved work, explicit HAWM state, separate CFC checks and auditable reports. It is not yet the full SaaS.

## v0.1 scope

1. Account identity contract.
2. Workspaces and conversations.
3. Persistable chat records with the explicit boundary:
   - `MODEL_REPLY_UNCHECKED`
   - `CFC NOT_CONNECTED_C2`
4. Persistable HAWM snapshots.
5. Persistable frozen CFC run records.
6. Audit-report metadata.
7. Usage-event records for later plan limits.

## Non-goals

- No password storage or custom authentication implementation.
- No provider API-key persistence.
- No billing implementation yet.
- No team roles yet.
- No mobile app.
- No change to frozen CFC.
- No claim that ordinary chat is CFC-authorized.

## Security boundary

Authentication should be delegated to a proven external identity provider. Provider API keys remain BYOK and must not be persisted by the Pro Beta data model unless a later, separately reviewed secret-storage design explicitly introduces that capability.

## Next implementation gate

Before wiring this into the hosted app:

- contracts tests must pass;
- persistence backend must preserve ownership boundaries;
- API-key fields must remain absent from persisted records;
- frozen CFC raw result and presentation must remain distinct;
- ordinary model replies must remain explicitly marked unchecked.
