# Decisions

## Unknown timing is not a pass

A stage that never reports completion yields `INCOMPLETE`, not “probably okay.”

## Metrics cannot hold transcript text

The log object has no transcript field. It is harder to leak something that the type cannot represent.

## WAV-only is deliberate

This proof is about the boundary, not codec coverage. Supporting every media format would make the public example larger while making the rule harder to see.

## Reject with a specific reason

“Invalid audio” is not useful enough for operators or tests.

> In realtime systems, “eventually correct” can still be wrong.
