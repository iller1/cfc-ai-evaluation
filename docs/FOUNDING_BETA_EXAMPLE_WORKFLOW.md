# CFC + HAWM Founding Beta — Example Workflow

## Example: AI research conclusion before business action

### Scenario

A team uses an AI assistant to summarize evidence about a supplier, policy, technical dependency, market fact or operational decision.

The AI produces a confident conclusion.

Before the team acts, CFC + HAWM is used to test whether the available evidence state actually supports closure.

## Input state

The user records:

- the AI conclusion,
- the evidence items relied upon,
- source freshness/status where known,
- conflicts or unresolved items,
- the intended action if the conclusion is accepted.

Example:

- Source A: current and supports the claim.
- Source B: contradicts the claim.
- Freshness/status of Source B: unknown.
- No rule says unknown freshness means stale.
- Proposed AI conclusion: "The claim is verified."

## Expected control behavior

The system should not silently convert unknown freshness into invalidity.

The expected state is unresolved until:
- Source B is shown to be stale/withdrawn/invalid under an explicit rule, or
- the conflict is otherwise resolved by valid evidence or authority.

The human remains responsible for the final decision.

## Beta run

1. Create or select the conversation/workspace.
2. Capture the model reply.
3. Preserve the relevant evidence state and HAWM snapshot.
4. Run the available CFC control/evaluation step.
5. Store the result together with version/provenance.
6. Human reviews the result.
7. Record whether the system:
   - stopped correctly,
   - stopped unnecessarily,
   - failed to stop,
   - produced an unclear result.

## Feedback examples

### Correct stop

The system returns unresolved because the contradictory source remains active or not safely dismissible.

Feedback classification:
- no bug,
- useful control event.

### False stop

The system blocks despite a supplied and valid rule that clearly resolves the contradiction.

Feedback classification:
- FALSE_STOP,
- investigate rule handling / scope / provenance.

### Missed stop

The system permits closure by treating unknown freshness as stale without supporting evidence.

Feedback classification:
- MISSED_STOP,
- PREMATURE_CLOSURE,
- high-priority regression case.

### Usability problem

The control state is technically correct but the user cannot tell why action was blocked.

Feedback classification:
- USABILITY,
- explanation/presentation issue.

## Re-test loop

For any defect or boundary finding:

1. preserve the original case;
2. record exact product/controller version;
3. reproduce it;
4. implement only an allowed change outside frozen artifacts;
5. re-run the same case;
6. run regression tests;
7. record the new result and changelog entry.

## Success criterion

The workflow is beta-useful when a company can:
- understand what the system is checking,
- reproduce why a case stopped or did not stop,
- retain human control,
- report a problem with enough context for us to reproduce it.
