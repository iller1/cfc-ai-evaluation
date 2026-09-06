# External Usability Tests

The Integration Layer RC has reached the point where further internal optimization would risk designing around author familiarity rather than real first-use friction.

Two bounded external tests are therefore defined.

## Test 1 — First CFC decision

Target gate:

`TIME_TO_FIRST_CFC_DECISION <= 15 minutes`

Tester requirements:

- comfortable with Python and pip;
- no prior hands-on CFC integration experience;
- no live assistance from the author during the timed attempt;
- frozen controller must not be modified.

Test case:

- AI conclusion: `APPROVED`
- evidence item 1: `verified`
- evidence item 2: `missing`
- required evidence items: `2`

Required semantic outcome:

`STOP`

Status: **READY FOR EXTERNAL TEST / NOT YET VERIFIED**

## Test 2 — First domain mapping

Exploratory target gate:

`TIME_TO_FIRST_DOMAIN_MAPPING <= 30 minutes`

The tester receives a small synthetic vendor record plus explicit business rules and must create an inspectable declarative mapping that yields:

- complete case → `ALLOW`
- missing-insurance case → `STOP`

The tester must not modify frozen CFC Anchor or rely on hidden custom logic to replace the supplied mapping mechanism.

Status: **READY FOR EXTERNAL TEST / NOT YET VERIFIED**

## Interpretation

One PASS supports only one bounded first-use observation.

Broader claims about ease of integration require multiple unfamiliar testers and preservation of failures, delays, confusion, and abandoned attempts as well as successful runs.

The v0.4 RC must remain unchanged during a given test attempt. Material fixes belong in a successor candidate.
