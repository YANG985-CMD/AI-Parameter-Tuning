# AI tuning safety contract

AI assistance is an experiment orchestrator and parameter proposer, not a direct actuator controller.

## Before live operation

- Obtain explicit authorization for this hardware run and identify the operator.
- Verify independent overpressure/overcurrent protection, emergency stop, watchdog, mechanical limits, and safe vent/disable behavior.
- Establish conservative parameter bounds from engineering analysis and low-energy tests.
- Confirm sensor plausibility, polarity, units, channel mapping, firmware version, and protocol schema.
- Run the complete host workflow in dry-run or replay mode.

## Trial state machine

```text
IDLE -> configure bounded candidate -> arm low-energy trial -> monitor -> IDLE
                                             | fault/timeout/link loss
                                             v
                                      emergency safe state
```

- Send `IDLE` before configuration and in a `finally` block.
- Change one defined candidate vector per trial and retain the last-known-safe vector.
- Require stable telemetry/handshake before arming.
- Stop on missing frames, sequence gaps beyond policy, sensor invalidity, limit approach, firmware fault, or operator request.
- Apply firmware-side limits even if the host validates the same values.
- Never automatically widen a bound because an optimizer requests it.

## Optimization records

Store the proposed and applied values separately, raw data, derived metrics, constraint violations, trial ID, software/firmware versions, and termination reason. Penalize unsafe or incomplete trials; never teach the optimizer that a truncated unsafe run is a good result.

Use tracking error, overshoot, settling, control effort, saturation ratio, thermal/load margin, dropped frames, and fault counts as multi-objective evidence. Require human review before promoting a candidate to a new baseline.

