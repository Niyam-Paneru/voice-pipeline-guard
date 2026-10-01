# Invariants

1. **Oversized input is rejected without fully buffering it.**
2. **Unsupported media fails with an explicit reason.**
3. **Incomplete timing data never counts as within budget.**
4. **Any over-budget required stage blocks display.**
5. **Metrics carry timing metadata, not transcript content.**
6. **Realtime usefulness is part of correctness.**

A perfect answer at the wrong time is still the wrong system behavior.
