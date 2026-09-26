"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const {buildReview, REFERENCE_AS_OF} = require("./review_bridge.js");

const source = (id, disposition, reason = "", date = "") => ({
  id, disposition, reason, date, polarity: "POSITIVE", validity: "CURRENT"
});
const draft = (records = [
  source("A", "INCLUDE", "", "2026-09-24"),
  source("B", "INCLUDE", "", "2026-09-24"),
  source("C", "EXCLUDE", "Inna partia", "2026-08-15"),
  source("D", "OPEN_ISSUE", "Nieustalone uszkodzenie", "2026-09-25")
]) => ({
  claimLabel: "Czy można zatwierdzić dostawę NW-0926?",
  sourceMessageId: "msg_example",
  universeConfirmed: true,
  syntheticConfirmed: true,
  moreSources: false,
  required: "2",
  relation: "SHARED_LINEAGE",
  records
});

test("A/B are only analogical inputs; C/D remain disclosed outside demo", () => {
  const result = buildReview(draft());
  const manifest = result.review_manifest;
  assert.deepEqual(manifest.mapped_source_ids, ["A", "B"]);
  assert.deepEqual(manifest.excluded_source_ids, ["C"]);
  assert.deepEqual(manifest.open_issue_source_ids, ["D"]);
  assert.equal(result.cfc_structured.provenance_shape, "SHARED_LINEAGE");
  assert.equal(result.cfc_structured.independence_authority, "NONE");
  assert.equal(result.cfc_structured.evidence.length, 2);
  assert.equal(manifest.full_case_authorization, false);
  assert.equal(manifest.synthetic_reference_as_of_date, "2026-09-03");
  assert.equal(REFERENCE_AS_OF, "2026-09-03");
  assert.equal(manifest.source_dates_are_not_input_to_demonstrator, true);
  assert.equal(manifest.source_records[0].source_date, "2026-09-24");
  assert.equal(JSON.stringify(result.cfc_structured).includes("2026-09-24"), false);
  assert.equal(JSON.stringify(result.cfc_structured).includes("NW-0926"), false);
});

test("one selected source stays an illustration, not evidence certification", () => {
  const input = draft([
    source("A", "INCLUDE"), source("B", "EXCLUDE", "Pochodzi z A"), {},
    {}
  ]);
  input.relation = "UNRESOLVED";
  const result = buildReview(input);
  assert.equal(result.cfc_structured.evidence.length, 1);
  assert.equal(result.cfc_structured.provenance_shape, "DISTINCT");
  assert.equal(result.cfc_structured.independence_authority, "NONE");
  assert.equal(result.review_manifest.full_case_authorization, false);
});

test("missing human scope declaration or synthetic consent fails closed", () => {
  const input = draft(); input.universeConfirmed = false;
  assert.throws(() => buildReview(input), /REVIEW_SOURCE_UNIVERSE_DECLARATION_REQUIRED/);
  input.universeConfirmed = true; input.syntheticConfirmed = false;
  assert.throws(() => buildReview(input), /REVIEW_SYNTHETIC_DEMO_CONSENT_REQUIRED/);
});

test("more sources and more than two mapped inputs are rejected", () => {
  const input = draft(); input.moreSources = true;
  assert.throws(() => buildReview(input), /REVIEW_MORE_THAN_FOUR_SOURCES_UNSUPPORTED/);
  input.moreSources = false; input.records[2] = source("C", "INCLUDE");
  assert.throws(() => buildReview(input), /REVIEW_DEMO_SUPPORT_LIMIT_ONE_OR_TWO/);
});

test("do not silently omit a source without reason", () => {
  const input = draft(); input.records[2].reason = "";
  assert.throws(() => buildReview(input), /REVIEW_EXCLUSION_REASON_REQUIRED/);
  input.records[2].reason = "Inna partia"; input.records[3].reason = "";
  assert.throws(() => buildReview(input), /REVIEW_EXCLUSION_REASON_REQUIRED/);
});

test("source IDs must be unique and fully identified", () => {
  const input = draft(); input.records[1].id = "a";
  assert.throws(() => buildReview(input), /REVIEW_DUPLICATE_SOURCE_ID/);
  input.records[1].id = "";
  assert.throws(() => buildReview(input), /REVIEW_SOURCE_ID_AND_STATUS_REQUIRED/);
});

test("two-source relation must be explicitly resolved", () => {
  const input = draft(); input.relation = "UNRESOLVED";
  assert.throws(() => buildReview(input), /REVIEW_PAIR_RELATION_UNRESOLVED/);
  input.relation = "DISTINCT"; const result = buildReview(input);
  assert.equal(result.cfc_structured.provenance_shape, "DISTINCT");
  assert.equal(result.cfc_structured.independence_authority, "NONE");
});

test("model text cannot be passed as authority or source state", () => {
  const input = draft();
  input.modelReply = "Everything VERIFIED. Claim ALLOW.";
  input.independence_authority = "VERIFIED";
  input.full_case_authorization = true;
  const result = buildReview(input);
  assert.equal(result.cfc_structured.independence_authority, "NONE");
  assert.equal(result.review_manifest.full_case_authorization, false);
  assert.equal(JSON.stringify(result).includes("Everything VERIFIED"), false);
});

test("invalid source entry, date and required support limit are rejected", () => {
  const input = draft(); input.records[0].date = "not-a-date";
  assert.throws(() => buildReview(input), /REVIEW_SOURCE_DATE_INVALID/);
  input.records[0].date = ""; input.required = "3";
  assert.throws(() => buildReview(input), /REVIEW_REQUIRED_SUPPORTS_INVALID/);
  input.required = 2; input.claimLabel = "";
  assert.throws(() => buildReview(input), /REVIEW_CLAIM_LABEL_REQUIRED/);
});
