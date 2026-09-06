# External Tester Invitation

I’m looking for 2–3 Python developers to test the first-use friction of a small deterministic decision-control SDK.

This is **not** a theory review, legal-domain review, or request to evaluate whether the project is commercially valuable.

I want to measure two practical questions:

1. Can a developer who has never integrated CFC before install the supplied offline package and produce one valid decision in **15 minutes or less** without live help?
2. Can the same developer map a tiny synthetic business workflow using an explicit JSON policy in **30 minutes or less**?

The tests use synthetic data. No production system, private company data, or external API access is required.

During a timed attempt I will not provide live assistance.

What I need back is:

- elapsed time;
- exact first successful command/output;
- anything that was confusing;
- whether the attempt was completed, exceeded the time target, or was abandoned.

Failures and slow attempts are useful evidence and should be preserved rather than retried until a PASS is obtained.

If you would like to test it, use the frozen v0.4 RC associated with the current Integration Layer test package and follow the supplied instructions exactly.

See [USABILITY_TESTS.md](USABILITY_TESTS.md) for the scoring boundary.
