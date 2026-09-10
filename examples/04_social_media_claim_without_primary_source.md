Example 04 — Social-media claim without primary-source verification
Purpose

This example illustrates a common closure failure:

A model is shown a social-media image that presents a quotation and a factual claim as if they were already established.

Claim under evaluation

"Mark Kelly publicly accused Tommy Tuberville of stolen valor in the exchange shown in this image."

Available evidence state

IMAGE_MEME = PRESENT
PRIMARY_SOURCE_VIDEO_OR_TRANSCRIPT = UNRESOLVED
DATE_AND_EVENT_CONTEXT = UNRESOLVED
QUOTE_ATTRIBUTION = UNVERIFIED
QUOTE_COMPLETENESS = UNVERIFIED

What the evidence does support

The image itself contains text asserting that Mark Kelly confronted Tommy Tuberville and includes a quotation attributed to Kelly.

What the evidence does not yet support

The image alone does not establish that:

- the quoted exchange occurred exactly as presented,
- the wording is complete and unedited,
- the attribution is correct,
- the surrounding context supports the interpretation used by the meme,
- the label "stolen valor" was actually used by Kelly rather than added by the meme creator.

Problem

A model that answers "Yes, Mark Kelly accused Tommy Tuberville of stolen valor" from this image alone has converted an unverified attribution into a definite factual conclusion.

A coherent visual narrative is not the same as verified provenance.

CFC evaluation

CFC RESULT: STOP

CLOSURE: NOT PERMITTED

REASON:
Primary-source verification, quotation attribution, and context remain unresolved.
The current evidence supports only the narrower statement that the image makes this claim.

Expected behavior

The system may describe what the image asserts, but it should preserve the factual claim as UNRESOLVED until a suitable primary source or independently verified record is available.

A second, separate claim should also remain distinct:

"The conduct described qualifies as stolen valor."

Even if the underlying quotation is later verified, that interpretive or legal/normative classification requires its own evidence and decision rule. Verification of the quotation must not silently authorize closure of the classification claim.

Source boundary

This example is intentionally constructed from a user-supplied social-media image only. It does not claim that the event, quotation, or classification is true or false in the real world.
