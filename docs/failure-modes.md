# Failure modes

## Oversized audio
The payload exceeds the configured bound. Response: stop after the bounded probe instead of buffering the whole body.

## Reader ignores requested byte count
A custom input reader may return far more bytes than `read(n)` requested. A size-limited probe must not append the entire returned object. Response: slice every chunk to the remaining `max_bytes + 1` probe allowance before copying it, then reject oversized captures.

## Unsupported or malformed audio
The capture does not satisfy the public WAV contract. Response: return a specific rejection reason.

## Stage never completes
Timing data is incomplete. Response: verdict remains incomplete and output is not displayable.

## Stage exceeds budget
The answer may be correct but too late. Response: suppress display.

## Transcript leaks into telemetry
Text content enters metrics. Response: metric types intentionally have no transcript field.

## Duration exceeds interaction budget
Audio is valid but too long for the intended realtime path. Response: reject before downstream work.
