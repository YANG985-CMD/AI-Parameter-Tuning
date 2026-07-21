# Portable embedded integration

Keep protocol logic independent of vendor APIs. Implement a portable core for packing frames, parsing commands, checking bounds, and tracking state; connect it through a small platform adapter.

## Platform adapter contract

Provide equivalents of these operations:

```text
serial_start_receive()
serial_write_nonblocking(bytes, length)
serial_tx_busy()
monotonic_time_ms()
enter_critical() / exit_critical()
request_safe_idle(reason)
```

The adapter may target STM32 HAL/LL, ESP-IDF, Arduino, Zephyr, FreeRTOS, RT-Thread, NXP MCUXpresso, TI C2000/CCS, Raspberry Pi/Linux serial, a DSP, FPGA soft core, or another SDK. Preserve protocol behavior across platforms even when driver details differ.

## Receive path

- Receive bytes by interrupt, DMA, polling, USB CDC, or OS serial API as appropriate.
- In interrupt context, only buffer data and signal deferred processing.
- Parse and dispatch complete commands outside time-critical control code.
- Bound buffers, reject overflowed lines, recover at the next terminator, and count errors.
- Restart or recover reception after driver errors without disabling the hardware safety path.

## Transmit path

- Produce telemetry from a periodic background task or main loop, not a fast control ISR.
- Snapshot shared controller state consistently before packing it.
- Prefer nonblocking/DMA transmission when available; skip and count a frame when TX is busy.
- Apply platform-specific cache maintenance and memory placement only where required.
- Document baud rate, byte format, endianness, schema, and update period.

Check bandwidth before choosing a rate. For conventional UART 8-N-1:

```text
bits_per_second = packet_bytes * frames_per_second * 10
```

Leave margin for commands and jitter. A 116-byte, 40 Hz packet consumes about 46.4 kbit/s.

## Single-owner mode switching

One serial endpoint normally cannot be opened by VOFA+ and a Codex/AI client simultaneously.

1. Stop streaming and place the controller in a safe idle state.
2. Close the current desktop application's serial connection.
3. Open the same port in the other application with identical UART settings.
4. Select the matching firmware protocol mode before interpreting data.

Do not add a software port splitter by default: duplicated or interleaved traffic can corrupt framing and makes control ownership ambiguous. If simultaneous visualization and tuning is a real requirement, use two physical/logical interfaces or let the AI client visualize and log the tuning telemetry itself.

## Platform-specific notes

- On cache-enabled MCUs such as STM32H7, align DMA buffers, place them in DMA-accessible RAM, and clean the appropriate cache range before TX.
- On USB CDC, handle host disconnects and partial writes explicitly.
- On Linux devices, use exclusive port ownership where supported and restore termios settings on exit.
- On small bare-metal MCUs, use fixed-size buffers and avoid dynamic allocation.
