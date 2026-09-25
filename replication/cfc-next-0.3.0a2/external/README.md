# External replication — CFC-next 0.3.0a2

This directory is for an unfamiliar reviewer who wants to reproduce the frozen
0.3.0a2 result from the canonical frozen Git ref rather than from moving
`main`.

## 1. Obtain the repository

Clone the repository normally, then create a separate frozen checkout:

```bash
git fetch origin
git worktree add ../cfc-next-0.3.0a2-frozen frozen/cfc-next-0.3.0a2
```

The expected checkout commit is:

`568282c1f66af9f1f2fad8cf2b04b08226b9aea6`

## 2. Run the verifier

From a current checkout containing this external replication verifier:

```bash
python replication/cfc-next-0.3.0a2/external/verify_external_replication.py \
  --repo ../cfc-next-0.3.0a2-frozen
```

The verifier first checks the frozen checkout identity and source hash, then
runs the frozen acceptance, promotion-readiness, state-isolation, and
freeze-review harnesses inside that checkout.

## 3. Expected result

Overall:

`"status": "PASS"`

Expected bounded results:

- positive fixtures: 14/14;
- negative controls: 12/12 fail-closed;
- unexpected BOUND negative paths: none;
- promotion-readiness: all gates pass;
- state-isolation: 14 tested relations, no candidate authorization visible to
  ordinary frozen evaluation;
- freeze manifest: verified.

## 4. Report independently

Use `EXTERNAL_REVIEW_RESULT_FORM.md`.

Please report reproduction failure separately from disagreement with the
project's interpretation. If a command fails, preserve the first failure and
the full generated output rather than manually editing the expected results.
