# VOFA+ manual tuning

Use VOFA+ as the only owner of the serial port. The device may continuously send JustFloat telemetry while VOFA+ sends ASCII tuning commands in the opposite direction. Do not let the device echo unframed text into the JustFloat receive stream.

## Generate the setup sheet

Copy and adapt `assets/vofa-manual-tuning-example.json` to the target device command grammar and proven parameter bounds. Then run:

```bash
python scripts/generate_vofa_manual_tuning.py profile.json --output vofa-setup.md
```

The generated sheet contains the exact Str-mode command templates, CRLF/LF ending, slider ranges, defaults, steps, buttons, and setup order. Review it against the firmware parser before configuring VOFA+.

## Configure VOFA+

1. Select the device serial port, baud rate, and JustFloat data engine.
2. Add Str commands from the generated sheet. VOFA+ replaces `%f` with a bound control's floating-point value.
3. Bind each slider to its command; copy its minimum, maximum, and step.
4. Bind apply, restore, and safe-stop commands to clearly labeled buttons.
5. Name telemetry channels and bind them to waveform widgets.
6. Test disconnected or at low energy before normal operation.

Official references:

- [VOFA+ data, commands, and parameters](https://www.vofa.plus/docs/learning/start/data_cmd_parameter/)
- [VOFA+ JustFloat](https://www.vofa.plus/docs/learning/dataengines/justfloat/)
- [VOFA+ slider](https://www.vofa.plus/docs/learning/widgets/slider/)
- [VOFA+ bound button](https://www.vofa.plus/docs/learning/widgets/bound_bt/)

## Device requirements

- Accept only documented command names and exact argument counts.
- Reject malformed, non-finite, and out-of-range values.
- Apply bounds in firmware even though the VOFA+ slider also has limits.
- Provide safe idle, restore, and command-timeout behavior.
- Keep live parameters separate from saved defaults until an explicit apply/save action.
