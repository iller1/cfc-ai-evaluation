# CFC + HAWM Founding Beta v2 — Deletion SOP

**Status:** operational procedure for Founding Beta measurement records.

## Scope

This procedure covers Founding Beta measurement records stored by CFC + HAWM.

It does not claim deletion from third-party model providers or other systems controlled by the customer/provider.

## Self-service path

Authenticated workspace owners have a dedicated deletion path:

`DELETE /api/workspaces/{workspace_id}/beta-measurements`

The API:
- verifies authentication;
- verifies workspace ownership;
- deletes Founding Beta measurement records for that workspace;
- returns the number of deleted records;
- reports `customer_content_deleted: 0` because the dedicated Founding Beta path is not intended to persist customer content.

## Operator-assisted request

If a customer requests deletion through support:

1. Record request ID and timestamp.
2. Confirm requester identity and workspace ownership.
3. Ask whether the request covers:
   - Founding Beta measurements only;
   - account/workspace closure;
   - any separately approved diagnostic exception.
4. Do not ask the customer to resend source documents or sensitive material.
5. Execute the applicable deletion path.
6. Verify the records are no longer returned for that workspace.
7. Record completion timestamp.
8. Send deletion confirmation to the verified requester.

## Diagnostic exceptions

If customer content was ever retained under a separately approved diagnostic exception, it must have:
- a documented purpose;
- exact storage location;
- owner;
- retention period;
- deletion procedure.

A diagnostic exception must not be assumed to be covered by the normal measurement deletion endpoint unless verified.

## Backups

Backup deletion/expiry behavior is **TO VERIFY with Railway/provider documentation and legal review**.

Do not promise immediate physical deletion from backups until the provider behavior is confirmed.

## Target response

Operational target for Founding Beta measurement deletion requests:

- acknowledge promptly through the agreed support channel;
- complete normal measurement deletion as soon as reasonably practicable;
- legal/privacy response-time wording remains subject to UK counsel.

## Evidence

Deletion ownership and persistence behavior are covered by internal tests on the Founding Beta branch.

This procedure is operational documentation, not a legal privacy-rights statement.
