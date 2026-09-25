# Stale relation subject relevance review

## Goal

Test whether the open relation-level stale authorization boundary requires stale E2
to remain about the same claim subject.

Hold constant:

- conclusion = POSITIVE for `DemoSubject`;
- E1 = POSITIVE / CURRENT / DemoSubject;
- E1 alone satisfies required supports = 1;
- E2 = POSITIVE / STALE;
- scope = EXPECTED;
- no explicit support-set independence certificate;
- both DemoSubject and OtherSubject identities are verified and installed in every case.

For E2, compare:

- SAME_SUBJECT: a fully bound record for DemoSubject;
- OTHER_SUBJECT: a fully bound record for OtherSubject.

Repeat that comparison with one minimal shared relation at a time:

1. common-mode group;
2. root-origin identity;
3. one generic dependency identity (`data_source`).

Total: **6 isolated fresh-process states**.

## Admissibility note

An earlier attempt to vary only E2 predicate was rejected before evaluation by the
frozen API because the mutated record was inadmissible under the
`GENERAL_RECORD_V5` authority/referent binding. That PR was closed without merge.

This review therefore changes the semantic target in a structurally valid way:
E2 receives its own verified identity, matching evidence subject, authority-record
entity binding, and provenance referent entity.

## Result

All six subject-relevance states completed successfully.

For each tested shared-relation family, SAME_SUBJECT and OTHER_SUBJECT were
identical:

### SAME_SUBJECT

- claim state = VERIFIED
- control closure = false
- false gates = [`decision_support_closure_valid`]
- no claim-support-policy violation
- no critical unresolved item
- no global-consistency violation
- no evidence, identity, or integration error

### OTHER_SUBJECT

- claim state = VERIFIED
- control closure = false
- false gates = [`decision_support_closure_valid`]
- no claim-support-policy violation
- no critical unresolved item
- no global-consistency violation
- no evidence, identity, or integration error

For all three relation families:

- same claim state = true;
- same control closure = true;
- same false gates = true.

## Classification

**CLAIM-SUBJECT-INSENSITIVE RELATION-LEVEL STALE AUTHORIZATION PERSISTENCE**

Within the tested boundary, the downstream authorization residue does not require
stale E2 to remain evidence about the claim subject.

Observed rule:

`stale E2 subject changes, shared relation held fixed -> authorization result unchanged`

Combined with the polarity review, the current evidence narrows the observed
mechanism to the existence of a shared historical provenance/dependency relation,
rather than the stale record's polarity or claim-subject identity.

This remains a boundary finding rather than a false-block classification. No
contractual claim is made here that the controller should ignore cross-subject
historical relations.
