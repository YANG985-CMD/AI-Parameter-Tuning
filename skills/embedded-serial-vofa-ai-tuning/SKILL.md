---
name: embedded-serial-vofa-ai-tuning
description: Build, adapt, debug, or review embedded serial communication that streams float telemetry to VOFA+ and supports safe AI-assisted controller parameter tuning. Use for STM32/HAL/FreeRTOS UART telemetry, VOFA JustFloat framing, Python serial clients, command protocols, experiment capture, bounded parameter proposals, safety interlocks, or converting an existing embedded serial implementation into a reusable host-device workflow.
---

# Embedded Serial VOFA AI Tuning

Implement two explicit lanes over a serial link:

1. Stream deterministic binary telemetry for VOFA+ curve display.
2. Run bounded, observable experiments for AI-assisted parameter tuning.

Keep the lanes logically separate even when they share one UART. Never interleave unframed ASCII responses with JustFloat packets.

## Workflow

1. Inspect the target UART, DMA/cache behavior, scheduler, telemetry fields, command parser, controller limits, fault handling, and physical emergency stop.
2. Choose a protocol profile. Do not assume a fixed channel count. Read [protocol.md](references/protocol.md).
3. For STM32/HAL/FreeRTOS integration, follow [stm32-integration.md](references/stm32-integration.md).
4. For AI tuning or any command that can move hardware, apply [ai-tuning-safety.md](references/ai-tuning-safety.md) before opening the port.
5. Use `scripts/serial_protocol.py` for host-side JustFloat parsing and bounded command construction. Extend its policy for the target controller instead of bypassing it.
6. Test parsers, framing, limits, timeouts, fault exits, and dry-run command generation without hardware first.
7. Require explicit user authorization before a live hardware run. Start in `IDLE`, apply one bounded candidate at a time, monitor every frame, and send `IDLE` in `finally`.

## VOFA+ lane

- Pack IEEE-754 `float32` values in documented order and endianness.
- Append the JustFloat tail `00 00 80 7F`.
- Keep frame size and channel schema synchronized between firmware, VOFA+, and host tools.
- Include a sequence number and protocol version for machine capture where possible.
- Rate-limit telemetry outside control ISRs; count dropped or busy transmissions.

## AI-tuning lane

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

