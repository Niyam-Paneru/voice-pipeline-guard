# Provenance

This package isolates two small rules from larger private voice-system work: bound audio capture before accepting it, and suppress display when timing evidence is incomplete or outside budget.

The public code includes synthetic WAV validation, explicit rejection reasons, per-stage timing budgets, display eligibility, and a metrics schema that intentionally has no transcript, answer-text, or audio-bytes field.

Provider SDKs, live audio, transcripts, credentials, clinic/customer context, transport code, and deployment plumbing are not included.

The repository demonstrates these guards under synthetic inputs. It makes no claim about current production latency, call quality, provider uptime, or deployment state.
