# Realtime latency contract

The public gate treats timing as part of result validity.

| Stage state | Verdict |
|---|---|
| no stages recorded | incomplete |
| required stage has no completion time | incomplete |
| any required stage exceeds its budget | exceeded budget |
| all required stages complete inside budget | within budget |

Only the final state is displayable.

This does not claim one universal latency budget for every voice product. It demonstrates the rule that a product-defined budget must be explicit and fail closed when timing evidence is missing.

## Precision and invalid measurements

Compare elapsed time at full floating-point precision. A 100.4 ms observation
exceeds a 100 ms budget even if the displayed report might be rounded elsewhere.
Missing, backward, NaN, infinite, or overflowed timing evidence is incomplete;
invalid (negative or non-finite) budgets are also incomplete. An incomplete
stage is **never** marked as passing in the per-stage report.

Elapsed time is reported as a float in milliseconds; existing whole-millisecond
observations remain numerically equal to their previous integer values.
