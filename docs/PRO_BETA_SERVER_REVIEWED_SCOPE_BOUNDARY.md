# Pro Beta — authenticated server-reviewed synthetic scope (v1)

This change closes one specific gap in PR #66: the previous guided flow validated mappings in the browser and POSTed arbitrary HAWM state to the generic endpoint. The new flow POSTs only user selections to `/api/conversations/{id}/reviewed-demo-scope`. The API verifies the authenticated conversation, verifies that a selected model response really belongs to it, revalidates all inputs, and derives the canonical HAWM review manifest and synthetic CFC configuration **on the server**.

It is NOT source authentication, independent source certification, a real-case evidence-state controller, or a decision to approve shipment NW-0926.

## Contract

Request shape: exactly `{"review": ..., "working_state": ...}`.

The review has explicit fields `claimLabel`, `sourceMessageId`, `universeConfirmed`, `syntheticConfirmed`, `moreSources`, `required`, `relation`, and four `records` with id/date/disposition/reason/polarity/validity. All fields are bounded and whitelisted. More than four known sources, more than two included demo records, duplicate IDs, invalid dates, unresolved pair relation, unexplained excluded/open records, or missing acknowledgements fail closed. No arbitrary authority or CFC config from the browser is accepted. Whitelisted HAWM free-text working fields are limited to 2,000 chars each.

If `sourceMessageId` is provided, it must be the ID of an owned assistant message in that conversation, from a provider, still labelled `MODEL_REPLY_UNCHECKED / NOT_CONNECTED_C2`. The server binds its ID and SHA-256 content fingerprint to the human declaration. It does not elevate its claims to evidence.

Only after validation is a snapshot saved as `USER_WORKING_STATE`. The server returns:

- snapshot ID;
- canonical review manifest with all included, excluded and open source IDs, original date strings and an explicit schema-only validation label;
- synthetic `cfc_structured` mapping derived on the server with `independence_authority=NONE`, fixed demo scope and at most two demo evidence shapes;
- `real_case_status=REAL_CASE_NOT_CHECKED`.

The browser checks these boundary fields before making a **separate explicit** call to the existing synthetic `cfc-from-hawm` route. It checks that the returned CFC response refers to that exact snapshot before associating it with the review. A mismatch fails closed. The actual persisted CFC-run schema still lacks durable snapshot/run linkage and this PR does not claim to fix it.

## What is deliberately NOT solved

- Validating that the document text is authentic or relevant to the real batch; PDF text extraction is not a source attestation.
- Establishing independent support, discovering a complete external evidence universe or resolving warehouse report D.
- Running a real claim against real date/scope. The current demonstration has `DemoSubject` and a fixed date of 2026-09-03.
- Disabling the legacy general-purpose HAWM endpoint or its separate demonstration controls; those retain their prior synthetic-only scope and should not be presented as server-attested reviewed submissions.
- Atomic snapshot/run persistence: a concurrent update can still intervene between POST requests; the browser verifies the returned snapshot ID and refuses to display a mismatched run as its own. Further persistence design is needed for audit-grade linkage.

## Release dependency

Railway production frontend tracks `main`, but API tracks `pro-beta-v0.1`. Do not deploy this frontend until the authenticated server route and validator have been separately integrated into that API production branch, checked against its retention/Postgres tests, and successfully deployed. Only then update frontend. No schema, frozen CFC, database, or unrelated service changes are required by this PR.

Run `python -m unittest -v pro_beta.test_reviewed_scope pro_beta.test_http_server pro_beta_frontend.test_frontend`, `node --test pro_beta_frontend/test_review_bridge.cjs`, and JavaScript syntax checks.
