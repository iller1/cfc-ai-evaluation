Example 03 — Conflicting Evidence Without Valid Resolution
Purpose

This example shows a case where active evidence records conflict and no valid resolution exists.

A model should not convert that conflict into a definite conclusion.

Evidence state

Record A: FORMALLY_POSITIVE
Record B: FORMALLY_NEGATIVE

Both records are ACTIVE and apply to the same required check.

No valid conflict-resolution record is available.

Model conclusion

"The claim is true."

Problem

The available evidence contains an unresolved conflict.

The model has selected one side of the conflict and produced a definite conclusion without a valid rule permitting that resolution.

Conflicting active evidence does not justify closure by itself.

CFC evaluation

CFC RESULT: STOP

CLOSURE: NOT PERMITTED

REASON:
The required check contains conflicting active evidence.
No valid conflict-resolution record resolves the conflict.
The current state therefore remains unresolved.

Expected behavior

CFC should preserve the unresolved state until the conflict is resolved by a valid and applicable resolution rule.

The framework should not choose the positive or negative record merely because one conclusion appears more plausible.
