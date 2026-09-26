"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const {buildReview, assessRealCaseReadiness, REFERENCE_AS_OF} = require("./review_bridge.js");

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
  input.records[0].date = "2026-02-31";
  assert.throws(() => buildReview(input), /REVIEW_SOURCE_DATE_INVALID/);
  input.records[0].date = ""; input.required = "3";
  assert.throws(() => buildReview(input), /REVIEW_REQUIRED_SUPPORTS_INVALID/);
  input.required = 2; input.claimLabel = "";
  assert.throws(() => buildReview(input), /REVIEW_CLAIM_LABEL_REQUIRED/);
});


test("real NW-0926 case remains NOT CHECKED and names every omitted source and temporal mismatch", () => {
  const manifest = buildReview(draft()).review_manifest;
  const assessment = assessRealCaseReadiness(manifest);
  assert.equal(assessment.status, "REAL_CASE_NOT_CHECKED");
  assert.equal(assessment.real_cfc_executed, false);
  assert.equal(assessment.real_decision_authorized, false);
  assert.deepEqual(assessment.scope.declared, ["A", "B", "C", "D"]);
  assert.deepEqual(assessment.scope.demo_included, ["A", "B"]);
  assert.deepEqual(assessment.scope.demo_excluded, ["C"]);
  assert.deepEqual(assessment.scope.open_issues, ["D"]);
  const codes = assessment.diagnostics.map(d => d.code);
  assert.ok(codes.includes("SOURCES_AFTER_SYNTHETIC_REFERENCE"));
  assert.ok(codes.includes("OPEN_SOURCE_ISSUES_NOT_RESOLVED"));
  assert.ok(codes.includes("SYNTHETIC_TWO_SOURCE_COVERAGE_LIMIT"));
  assert.ok(codes.includes("REAL_CFC_EVIDENCE_EXECUTION_NOT_CONNECTED"));
  assert.ok(assessment.diagnostics.some(d => d.code === "SOURCES_AFTER_SYNTHETIC_REFERENCE" && d.explanation.includes("A, B, D") && !d.explanation.includes("A, B, C, D")));
});

test("no review and manipulated flags never become real-case authorization", () => {
  const empty = assessRealCaseReadiness(null);
  assert.equal(empty.status, "REAL_CASE_NOT_CHECKED");
  assert.equal(empty.real_cfc_executed, false);
  assert.equal(empty.real_decision_authorized, false);
  assert.equal(empty.diagnostics[0].code, "NO_VALID_SOURCE_REVIEW");
  const manifest = buildReview(draft()).review_manifest;
  manifest.full_case_authorization = true;
  manifest.synthetic_independence_authority = "VERIFIED";
  manifest.universe_declared_by_user_not_externally_verified = false;
  const assessment = assessRealCaseReadiness(manifest);
  assert.equal(assessment.status, "REAL_CASE_NOT_CHECKED");
  assert.equal(assessment.real_decision_authorized, false);
  assert.ok(assessment.diagnostics.some(d => d.code === "SOURCE_AUTHORITY_AND_PROVENANCE_NOT_INSTALLED"));
});

test("sources with a date before synthetic reference do not cure missing real authority", () => {
  const rows = [source("A", "INCLUDE", "", "2026-08-01"), source("B", "INCLUDE", "", "2026-08-02"), {}, {}];
  const manifest = buildReview(draft(rows)).review_manifest;
  const assessment = assessRealCaseReadiness(manifest);
  assert.equal(assessment.real_decision_authorized, false);
  assert.ok(!assessment.diagnostics.some(d => d.code === "SOURCES_AFTER_SYNTHETIC_REFERENCE"));
  assert.ok(assessment.diagnostics.some(d => d.code === "REAL_CFC_EVIDENCE_EXECUTION_NOT_CONNECTED"));
});
