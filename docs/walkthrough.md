# Walkthrough: correct, but late

A voice turn enters as a valid bounded WAV capture.

The pipeline records:

- transcription: 1,180 ms against a 1,500 ms budget;
- retrieval: 210 ms against a 500 ms budget;
- final display stage: completion time missing.

The first two stages look healthy.

The third does not have enough evidence to say it completed inside budget.

So the verdict is **incomplete**, not “close enough.”

Now consider another turn where every stage completes but one stage exceeds its budget. The answer may still be semantically correct, but the realtime contract is broken and display is suppressed.

That is the point of the repo: timing evidence participates in correctness.
