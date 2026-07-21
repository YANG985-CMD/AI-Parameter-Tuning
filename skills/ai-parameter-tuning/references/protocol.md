# Serial protocol

## JustFloat framing

Encode each sample as contiguous little-endian IEEE-754 `float32` values followed by four bytes:

```text
payload = float32[channel_count]
tail    = 00 00 80 7F
```

Treat channel count and field order as a versioned schema. Search for the tail in a receive buffer, take exactly `4 * channel_count` preceding bytes, reject non-finite values or an unexpected version, then continue. A tail alone is not an integrity check; add CRC and an explicit binary header for noisy or safety-critical links.

## Exclusive host modes

Use one serial port owner at a time:

- **VOFA+ mode:** VOFA+ owns the port, receives JustFloat frames for live plots, and may send allowlisted manual tuning commands from bound controls. Do not run the Codex/AI serial client.
- **AI tuning mode:** Close VOFA+, then let the Codex-managed client own the port, receive the versioned experiment stream, and send bounded commands.

The AI client may plot or save its own curves, but it must not assume VOFA+ can share the open port. Simultaneous operation requires a second UART/USB CDC endpoint or an intentional framed multiplexer with one clear control owner.

For VOFA+ manual tuning, bind each button, slider, or parameter field to one documented device command. Keep command terminators and units explicit. Provide apply, restore, and safe-stop actions, and enforce the same bounds in firmware. Do not echo unframed ASCII replies into the device-to-host JustFloat stream.

The source project contains multiple valid profiles that illustrate why schemas must be configurable:

- Normal FreeRTOS VOFA view: 6 floats, selected angle/diagnostic values plus four pressures, normally 10 Hz.
- Synchronized experiment stream: 28 floats, normally 40 Hz.
- A separate `main.c` diagnostic path: 10 floats and DMA transmission.

Do not combine these definitions. Select one mode and keep firmware, VOFA+, and Python schema identical.

## Example 28-channel experiment schema

```text
protocol_version, sequence, time_ms, trial_id, marker, mode, armed, phase01,
hip_ref_deg, knee_ref_deg, hip_deg, knee_deg,
p1_target_kpa, p2_target_kpa, p3_target_kpa, p4_target_kpa,
p1_kpa, p2_kpa, p3_kpa, p4_kpa,
pwm1_percent, pwm2_percent, pwm3_percent, pwm4_percent,
hip_feedback_ok, knee_feedback_ok, fault_code, stream_active
```

## AI-mode ASCII commands

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
