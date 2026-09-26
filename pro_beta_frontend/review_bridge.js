/* A human-reviewed source-scope manifest for an ANALOGOUS SYNTHETIC demo, not evidence verification. */
(function (root) {
  "use strict";
  const REFERENCE_AS_OF = "2026-09-03";
  const dispositions = new Set(["INCLUDE", "EXCLUDE", "OPEN_ISSUE"]);
  const polarities = new Set(["POSITIVE", "NEGATIVE"]);
  const validities = new Set(["CURRENT", "STALE"]);

  function fail(code) { throw new Error(code); }
  function clean(value, limit) {
    const s = String(value == null ? "" : value).trim();
    if (s.length > limit) fail("REVIEW_FIELD_TOO_LONG");
    return s;
  }
  function buildReview(raw) {
    if (!raw || typeof raw !== "object") fail("REVIEW_REQUIRED");
    if (raw.moreSources) fail("REVIEW_MORE_THAN_FOUR_SOURCES_UNSUPPORTED");
    if (raw.universeConfirmed !== true) fail("REVIEW_SOURCE_UNIVERSE_DECLARATION_REQUIRED");
    if (raw.syntheticConfirmed !== true) fail("REVIEW_SYNTHETIC_DEMO_CONSENT_REQUIRED");
    if (!Array.isArray(raw.records) || raw.records.length !== 4) fail("REVIEW_FOUR_SLOTS_REQUIRED");
    const claimLabel = clean(raw.claimLabel, 160);
    if (!claimLabel) fail("REVIEW_CLAIM_LABEL_REQUIRED");
    const sourceMessageId = clean(raw.sourceMessageId, 128);
    const records = [];
    const ids = new Set();
    for (const entry of raw.records) {
      if (!entry || typeof entry !== "object") fail("REVIEW_RECORD_INVALID");
      const id = clean(entry.id, 64);
      const disposition = clean(entry.disposition, 32);
      const reason = clean(entry.reason, 400);
      const date = clean(entry.date, 10);
      if (!id && !disposition && !reason && !date) continue;
      if (!id || !dispositions.has(disposition)) fail("REVIEW_SOURCE_ID_AND_STATUS_REQUIRED");
      const key = id.toLowerCase();
      if (ids.has(key)) fail("REVIEW_DUPLICATE_SOURCE_ID");
      ids.add(key);
      if (date && !/^\d{4}-\d\d-\d\d$/.test(date)) fail("REVIEW_SOURCE_DATE_INVALID");
      if (disposition !== "INCLUDE" && !reason) fail("REVIEW_EXCLUSION_REASON_REQUIRED");
      const polarity = clean(entry.polarity, 16);
      const validity = clean(entry.validity, 16);
      if (disposition === "INCLUDE" && (!polarities.has(polarity) || !validities.has(validity))) {
        fail("REVIEW_INCLUDED_SOURCE_MAPPING_REQUIRED");
      }
      records.push({
        id, disposition, reason, source_date: date || null,
        // Polarity/validity are human-provided SIMULATION settings, not document attestations.
        demo_polarity: disposition === "INCLUDE" ? polarity : null,
        demo_validity: disposition === "INCLUDE" ? validity : null
      });
    }
    if (!records.length) fail("REVIEW_AT_LEAST_ONE_SOURCE_REQUIRED");
    const included = records.filter(r => r.disposition === "INCLUDE");
    if (!included.length || included.length > 2) fail("REVIEW_DEMO_SUPPORT_LIMIT_ONE_OR_TWO");
    const required = Number(raw.required);
    if (!Number.isInteger(required) || (required !== 1 && required !== 2)) fail("REVIEW_REQUIRED_SUPPORTS_INVALID");
    const relation = clean(raw.relation, 24);
    if (included.length === 2 && !["DISTINCT", "SHARED_LINEAGE"].includes(relation)) {
      fail("REVIEW_PAIR_RELATION_UNRESOLVED");
    }
    const shape = included.length === 2 ? relation : "DISTINCT";
    const manifest = {
      manifest_version: "HUMAN_REVIEWED_SYNTHETIC_DEMO_V1",
      claim_label_for_human_reference_only: claimLabel,
      model_reply_context_message_id: sourceMessageId || null,
      universe_declared_by_user_not_externally_verified: true,
      source_records: records,
      mapped_source_ids: included.map(r => r.id),
      excluded_source_ids: records.filter(r => r.disposition === "EXCLUDE").map(r => r.id),
      open_issue_source_ids: records.filter(r => r.disposition === "OPEN_ISSUE").map(r => r.id),
      synthetic_reference_as_of_date: REFERENCE_AS_OF,
      source_dates_are_not_input_to_demonstrator: true,
      analogous_settings: {required_independent_supports: required, provenance_shape: shape},
      synthetic_independence_authority: "NONE",
      full_case_authorization: false,
      boundary: "SOURCE_SCOPE_HUMAN_REVIEWED_ANALOGOUS_SYNTHETIC_CFC_ONLY"
    };
    const cfcStructured = {
      conclusion: "POSITIVE",
      required_independent_supports: required,
      provenance_shape: shape,
      independence_authority: "NONE",
      scope: "EXPECTED",
      evidence: included.map(r => ({
        polarity: r.demo_polarity, validity: r.demo_validity
      }))
    };
    return {review_manifest: manifest, cfc_structured: cfcStructured};
  }
  const api = Object.freeze({buildReview, REFERENCE_AS_OF});
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.ProBetaReviewBridge = api;
})(typeof window !== "undefined" ? window : globalThis);
