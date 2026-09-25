# CFC-next 0.3.0a1 process-isolation promotion review

## Purpose

Test whether the accepted experimental candidate can coexist safely with the
frozen CFC Anchor 0.2.90rc1 inside one Python interpreter.

This review does not modify the candidate or the frozen wheel.

## Promotion requirements

A promotable candidate must not make a frozen Controller instance observe
candidate admission semantics merely because the candidate module was imported.

The review therefore checks:

1. frozen engine registration function before candidate import;
2. engine registration function immediately after candidate import;
3. a FrozenController class loaded before candidate import;
4. candidate patch lifecycle after an explicit restore attempt;
5. fresh-process isolation control before and after the mutation probe.

## Interpretation

A process-local mutation is not the same as modifying the frozen wheel on disk.
However, promotion requires a stronger boundary than file immutability: frozen
and candidate semantics must not silently change each other inside a shared
runtime.

If import-time mutation contaminates the frozen Controller, the candidate
remains an accepted experimental candidate but is not ready to become a frozen
or release baseline until that isolation problem is repaired.
