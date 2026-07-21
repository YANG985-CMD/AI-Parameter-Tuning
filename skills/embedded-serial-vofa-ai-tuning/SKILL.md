---
name: embedded-serial-vofa-ai-tuning
description: "Build, adapt, debug, or review portable embedded serial communication with two mutually exclusive host modes: VOFA+ JustFloat curve display or Codex/AI-assisted controller parameter tuning. Use for MCU, DSP, SoC, Arduino, bare-metal, RTOS, Linux-device, UART/USB-serial telemetry, command protocols, experiment capture, bounded parameter proposals, safety interlocks, or converting an existing device protocol into a reusable host-device workflow."
---

# Embedded Serial VOFA AI Tuning

Implement two mutually exclusive modes over one serial port:

1. Connect VOFA+ and stream deterministic JustFloat telemetry for curve display.
2. Disconnect VOFA+, connect the Codex-managed host client, and run bounded, observable AI-assisted tuning experiments.

Only one host may own the serial port at a time. Never instruct users to connect VOFA+ and Codex to the same port concurrently, and never interleave the two modes.

## Workflow

1. Identify the processor, SDK or framework, serial peripheral, scheduler, telemetry fields, command parser, controller limits, fault handling, and physical emergency stop.
2. Choose exactly one active host mode and a versioned protocol profile. Do not assume a fixed channel count. Read [protocol.md](references/protocol.md).
3. Implement the portable core and a thin platform adapter. Follow [embedded-integration.md](references/embedded-integration.md); use STM32/HAL only as one example.
4. For AI tuning or any command that can move hardware, apply [ai-tuning-safety.md](references/ai-tuning-safety.md) before opening the port.
5. Use `scripts/serial_protocol.py` for host-side JustFloat parsing and bounded command construction. Extend its policy for the target controller instead of bypassing it.
6. Test parsers, framing, limits, timeouts, fault exits, and dry-run command generation without hardware first.
7. Require explicit user authorization before a live hardware run. Start in `IDLE`, apply one bounded candidate at a time, monitor every frame, and send `IDLE` in `finally`.

## VOFA+ lane

- Require the Codex/AI serial client to close the port before VOFA+ opens it.
- Pack IEEE-754 `float32` values in documented order and endianness.
- Append the JustFloat tail `00 00 80 7F`.
- Keep frame size and channel schema synchronized between firmware, VOFA+, and host tools.
- Include a sequence number and protocol version for machine capture where possible.
- Rate-limit telemetry outside control ISRs; count dropped or busy transmissions.

## AI-tuning lane

- Require VOFA+ to close the port before the Codex-managed client opens it.
- Let AI propose parameters, never unrestricted actuator commands.
- Enforce an allowlist, numeric bounds, finite values, rate limits, and experiment duration on both host and firmware.
- Require health telemetry such as armed state, fault code, measured limits, stream state, and sequence number.
- Reject unsafe candidates before transmission and roll back to the last-known-safe set after failure.
- Preserve raw telemetry, candidate parameters, objective metrics, firmware/protocol version, and stop reason for every trial.

## Completion criteria

- Binary frames decode correctly across fragmented and noisy input.
- Unknown, malformed, non-finite, and out-of-range commands are rejected.
- The firmware has timeout/fault shutdown independent of the host.
- A disconnected or crashed host causes a safe idle state.
- Live tuning remains opt-in and cannot start from a script default.
- Mode ownership is explicit and a second host cannot silently attach.
