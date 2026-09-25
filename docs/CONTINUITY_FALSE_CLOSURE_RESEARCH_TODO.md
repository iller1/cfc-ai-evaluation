# CFC + HAWM — Continuity / False-Closure Research TODO

Source note: `eduardo_continuity_new_notes(1).pdf` (Continuity Science materials + our control interpretation).

## New research tasks

### 1. Build a FALSE CONTINUITY -> FALSE AUTHORIZATION -> FALSE CLOSURE benchmark

Goal:
- test whether a state that looks continuous can still be wrongly allowed to authorize a downstream step;
- separate continuity classification from downstream authorization.

Core chain:
`bad observation model / bad necessary constraint / missed separatrix -> false continuity state -> false state validity -> downstream authorization -> false closure`

### 2. Split the benchmark into four independently testable layers

- T1 — Justification path: does the result still belong to the original evidence?
- T2 — Continuity evidence: can a continuity test falsify without relying on a bad proxy?
- T3 — Boundary / separatrix: is the trajectory boundary detected correctly?
- T4 — Downstream authorization: does this state still have the right to authorize the next step?

### 3. Add explicit meta-control rules to the systems-theory model

- `Same endpoint != same path`
- `Same path appearance != same validity`
- `Valid state != authorized downstream use`
- `Correct state != justified state`
- `Preserved information != preserved justification`

### 4. Test the controller hierarchy

Model:
- Controller 1 evaluates the current state / claim.
- Controller 2 evaluates the validity of the trajectory, justification path and control basis.
- Authorization layer decides whether the result may influence the next step.

Expected fail-closed behaviour:
- invalid or unresolved trajectory/justification => downstream authorization withheld.

### 5. Attack the necessary-condition assumption

Test whether a supposed necessary continuity condition is actually only a proxy.

Failure classes:
- false falsification;
- missed breach;
- wrong continuity verdict;
- wrong downstream state;
- false closure.

### 6. Test separatrix / recoverability detection

Questions:
- can the system detect approach to a critical trajectory boundary before crossing?
- can a large perturbation remain recoverable while a small perturbation crosses the boundary?
- can false boundary detection create a false identity/state change?
- can missed crossing leave stale validity active?

### 7. Keep source claims and our inferences separate

Do not present these derived control-chain claims as Eduardo Filho's direct claims unless explicitly supported by his text.

## Priority

Next experimental candidate:

**FALSE CONTINUITY -> FALSE AUTHORIZATION -> FALSE CLOSURE**

Do not modify the frozen CFC controller for this work. Build it as an external synthetic/adversarial benchmark first.