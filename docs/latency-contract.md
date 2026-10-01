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
