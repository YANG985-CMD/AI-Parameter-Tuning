# Serial protocol

## JustFloat framing

Encode each sample as contiguous little-endian IEEE-754 `float32` values followed by four bytes:

```text
payload = float32[channel_count]
tail    = 00 00 80 7F
```

Treat channel count and field order as a versioned schema. Search for the tail in a receive buffer, take exactly `4 * channel_count` preceding bytes, reject non-finite values or an unexpected version, then continue. A tail alone is not an integrity check; add CRC and an explicit binary header for noisy or safety-critical links.

The extracted STM32 project contains multiple valid profiles:

- Normal FreeRTOS VOFA view: 6 floats, selected angle/diagnostic values plus four pressures, normally 10 Hz.
- Synchronized experiment stream: 28 floats, normally 40 Hz.
- A separate `main.c` diagnostic path: 10 floats and DMA transmission.

Do not combine these definitions. Select one mode and keep firmware, VOFA+, and Python schema identical.

## Extracted 28-channel experiment schema

```text
protocol_version, sequence, time_ms, trial_id, marker, mode, armed, phase01,
hip_ref_deg, knee_ref_deg, hip_deg, knee_deg,
p1_target_kpa, p2_target_kpa, p3_target_kpa, p4_target_kpa,
p1_kpa, p2_kpa, p3_kpa, p4_kpa,
pwm1_percent, pwm2_percent, pwm3_percent, pwm4_percent,
hip_feedback_ok, knee_feedback_ok, fault_code, stream_active
```

## ASCII command channel

Use one command per line, terminated by CRLF. Tokenize spaces, tabs, commas, or semicolons only when compatibility requires it. Prefer a strict grammar:

```text
COMMAND argument...\r\n
```

Add request IDs and framed `ACK`/`NACK` responses if acknowledgements share the UART. Otherwise place responses on another UART or suppress them during binary streaming.

Minimum firmware behavior:

- Reject unknown commands, wrong arity, non-finite values, and values outside firmware bounds.
- Report a stable error code; do not silently ignore invalid tuning commands.
- Process complete lines outside the receive ISR.
- Reset safely after overflow and restart reception after UART errors.
- Implement `IDLE`/`STOP`, a command watchdog, and a firmware-side fault latch.

