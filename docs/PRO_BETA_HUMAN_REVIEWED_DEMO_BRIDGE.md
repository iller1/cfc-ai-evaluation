# Pro Beta: human-reviewed AI → HAWM scope → synthetic CFC demonstration

## Why this exists

The ordinary AI chat response has authority `MODEL_REPLY_UNCHECKED / NOT_CONNECTED_C2`. The frozen Anchor is **not** a natural-language/document parser. The current `demonstrator/custom_case_runner.py` has a fixed subject `DemoSubject`, synthetic host authority verifiers, at most 2 evidence records, and an as-of date of `2026-09-03`. This reference date predates the illustrative NW-0926 documents dated 24–25 September 2026. A demonstration must never be presented as a real review of those documents.

## New bounded workflow

1. Select an AI answer via **Użyj jako kontekst przeglądu**. It is shown as untrusted text only; no extraction/mapping is performed.
2. Manually enter up to four *known* source identifiers, optional source dates, and one of `INCLUDE`, `EXCLUDE`, `OPEN_ISSUE` for each. Reasons are mandatory for excluded/open sources.
3. At most 2 can be mapped to an **analogous synthetic case**; the required supports are 1 or 2. For a pair, provenance relation must be explicitly described `DISTINCT` or `SHARED_LINEAGE`. Unknown relation blocks running this demo. A distinct-looking pair never automatically receives independence certification: `independence_authority=NONE` is immutable on this review path.
4. The user declares that all known sources are listed and separately acknowledges that the runner ignores actual source dates/texts. Having more than four sources blocks this bounded review path.
5. Save `review_manifest` (all entered identifiers and dispositions, mapped/excluded/open IDs, human-only claim label, user-selected model message reference, fixed demo reference date, `full_case_authorization=false`) alongside the exact two-or-one synthetic `cfc_structured` configuration in HAWM as `USER_WORKING_STATE`. The client then explicitly calls the existing `/cfc-from-hawm` endpoint, never a free-text inference route.
6. The live response `hawm_snapshot_id` must match the ID returned by the immediately preceding HAWM save before the UI displays that demonstration as associated with the review. Mismatch fails closed. The historical persisted run still lacks a durable binding to a snapshot.
7. UI displays returned frozen-controller `presentation.decision`, but always labels either `ALLOW` or `STOP` as **synthetic DemoSubject only**, and separately lists source IDs outside the analogous run. Source details are in the HAWM snapshot and existing complete Markdown audit report.

## NW-0926 example (illustration only)

| Source | User-selected disposition | Why |
|---|---|---|
| A | INCLUDE, positive/current in demo | Manufacturer report, 24 Sep |
| B | INCLUDE, positive/current in demo | Dependent on A; set pair relation SHARED_LINEAGE |
| C | EXCLUDE | Different batch; not part of the demo input |
| D | OPEN_ISSUE | Warehouse note about damage is unresolved, not consumed by the demo |

With `required_independent_supports=2`, the synthetic demonstrator receives exactly two positive/current source shapes, `SHARED_LINEAGE`, and `independence_authority=NONE`. Neither the claim text `NW-0926` nor the four actual documents, source dates, or unresolved D are sent as real CFC evidence. The manifest explicitly preserves these omissions. Even if any demo shows `ALLOW` in another configuration, `full_case_authorization=false` always applies.

## Contract boundaries and next real integration

- The frontend review validator guards this guided flow, not the existing general-purpose authenticated HAWM endpoint; it cannot replace a server-side trust boundary. Model-suggested mappings require independent human review and upstream source/provenance authority.
- This PR does NOT add backend/database/controller changes, attest independence, evaluate four real documents or link persisted CFC runs one-to-one to a specific HAWM snapshot. Returned `hawm_snapshot_id` exists per response, but historical persisted run binding is not provided in the current persistence schema. The UI explicitly discloses that limitation.
- A genuine real-case bridge requires: explicit real identity/claim/time/scope model; source-specific authenticity, referent and dependency records; certifying upstream authorities; complete source universe/relevance/conflicts; persistent snapshot→run binding; and fail-closed handling of D. Only then can the frozen Anchor be invoked through its public API with non-synthetic evidence. None is simulated by the current guided UI.

## Acceptance checks

Run `node --test pro_beta_frontend/test_review_bridge.cjs`, `node --check pro_beta_frontend/app.js`, and `python -m unittest -v pro_beta_frontend.test_frontend`. A date after 2026-09-03 may be preserved in the *human manifest* but must never be passed into the synthetic `cfc_structured` date-free configuration. The AI answer is copied into a text-only contextual preview and cannot become an attestation.
