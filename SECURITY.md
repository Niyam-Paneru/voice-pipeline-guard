# Security and privacy

The package contains no live audio, transcript data, provider credentials, or production endpoint.

The implemented privacy boundary is narrow and inspectable: capture is size/format bounded before acceptance, display requires complete timing evidence inside budget, and `UtteranceMetrics` has no field for transcript text, answer text, or audio bytes.

A real voice deployment would still need transport authentication, provider webhook validation, rate limits, appropriate PII/PHI handling, storage/retention controls, and incident logging. None of those are claimed by this repository.
