# STM32, HAL, and FreeRTOS integration

## Receive path

- Receive a byte or DMA chunk in the HAL callback.
- In ISR context, only append bytes, detect line completion, and signal a task.
- Copy and dispatch a completed command outside the ISR.
- Bound the buffer and discard an overflowed line until the next terminator.
- Restart reception in `HAL_UART_ErrorCallback` and expose error counters in telemetry.

## Transmit path

- Produce telemetry from a periodic low-priority task, not the control ISR.
- Snapshot shared control state consistently before packing it.
- Prefer DMA for larger/high-rate packets; skip or count a frame if TX is busy.
- On cache-enabled STM32H7, align DMA buffers to cache-line boundaries, place them in DMA-accessible RAM, and clean D-cache for the exact aligned range before TX.
- Document UART settings. The extracted implementation uses USART3 at 115200 baud, 8-N-1.

Check bandwidth before choosing a rate. Approximate UART use for 8-N-1 as:

```text
bits_per_second = packet_bytes * frames_per_second * 10
```

Leave margin for commands, jitter, and retransmission. A 116-byte, 40 Hz packet consumes about 46.4 kbit/s before other traffic.

## Concurrency

- Do not transmit two packet formats concurrently on one UART.
- Protect mode switches so a frame cannot change schema halfway through.
- Avoid blocking UART calls whose timeout can delay a control task.
- Keep telemetry failure non-fatal to control, but make loss visible through counters.

