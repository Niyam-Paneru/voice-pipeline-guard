# Design overview

Realtime voice has two correctness boundaries that are easy to mistake for “performance details.”

## 1. Bound the read before paying for it

A size limit checked after reading the entire upload is not a real memory bound.

The capture path requests only `max_bytes + 1` bytes, which is enough to distinguish “fits” from “too large” without materializing the whole oversized payload.

## 2. Latency can invalidate a correct result

A transcript can be correct and still arrive too late to be useful.

The latency gate therefore treats missing timing data and over-budget timing as non-displayable states.

The public package splits capture, latency, models, and metadata logging so each boundary can be reviewed independently.
