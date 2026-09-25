# Shared-lineage stale-record review

## Purpose

Resolve the remaining state-space Finding D:

> In SHARED_LINEAGE cases, adding a stale second record can appear to change
> authorization.

The original E2 OMIT -> INCLUDE comparison is not a clean one-factor mutation
because the custom fixture also rewrites E1 provenance into shared-lineage form
when the second record is introduced.

This review therefore uses a cleaner pair:

- E1 and E2 are present in both states;
- provenance remains SHARED_LINEAGE in both states;
- independence authority remains NONE;
- only E2 validity changes CURRENT -> STALE.

## Question

Does stale E2 itself continue to affect closure through dependency/common-mode
semantics, or was the earlier effect caused by the derived E1 provenance rewrite
that accompanied E2 addition?

## Interpretation boundary

This is an external semantic review over frozen CFC Anchor 0.2.90rc1.
The controller is not modified.
