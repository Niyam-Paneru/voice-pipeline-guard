# Verification

CircleCI uses Python 3.12 and installs `pytest` before running the public checks.

Run the same repository checks locally:

```bash
python -m compileall -q src
python -m pytest
PYTHONPATH=src python -m audio_guard.demo
```

Expected result: source compilation succeeds, the behavior tests pass, and the synthetic walkthrough completes without requiring a microphone, provider account, credentials, or live audio.

CircleCI also checks that the public boundary documents exist: `docs/invariants.md`, `docs/failure-modes.md`, `docs/verification.md`, `SECURITY.md`, and `PROVENANCE.md`.