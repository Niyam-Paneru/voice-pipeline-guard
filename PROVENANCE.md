# Provenance

This repository isolates bounded-audio and fail-closed latency rules from larger private voice-system work, including DentSignal and later local voice experiments.

## Preserved

- read bounds before buffering;
- explicit media rejection reasons;
- per-stage timing budgets;
- incomplete/late output suppression;
- metadata-only telemetry.

## Rewritten for public review

Provider SDKs, live audio, transcripts, credentials, clinic/customer context, and deployment plumbing are omitted.

## Claim boundary

This code demonstrates guard behavior under synthetic inputs. It does not claim current production latency, call quality, or provider uptime.
