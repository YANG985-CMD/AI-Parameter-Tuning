#!/usr/bin/env python3
"""Generate a concrete VOFA+ manual-tuning setup sheet from JSON."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


class ProfileError(ValueError):
    pass


def _number(value, field: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise ProfileError(f"{field} must be numeric") from error
    if not math.isfinite(result):
        raise ProfileError(f"{field} must be finite")
    return result


def validate_profile(profile: dict) -> dict:
    if not isinstance(profile, dict):
        raise ProfileError("profile must be a JSON object")
    controls = profile.get("controls")
    if not isinstance(controls, list) or not controls:
        raise ProfileError("controls must be a non-empty list")
    line_ending = profile.get("line_ending", "CRLF").upper()
    if line_ending not in {"CRLF", "LF"}:
        raise ProfileError("line_ending must be CRLF or LF")

    names = set()
    validated = []
    for index, raw in enumerate(controls, 1):
        if not isinstance(raw, dict):
            raise ProfileError(f"control {index} must be an object")
        name = str(raw.get("name", "")).strip()
        widget = str(raw.get("widget", "")).strip().lower()
        command = str(raw.get("command", "")).strip()
        if not name or name in names:
            raise ProfileError(f"control {index} name must be non-empty and unique")
        names.add(name)
        if widget not in {"slider", "button"}:
            raise ProfileError(f"{name}: widget must be slider or button")
        if not command or not command.isascii() or "\r" in command or "\n" in command:
            raise ProfileError(f"{name}: command must be printable ASCII without line endings")

        item = {"name": name, "widget": widget, "command": command}
        if widget == "slider":
            if command.count("%f") != 1:
                raise ProfileError(f"{name}: slider command must contain exactly one %f")
            minimum = _number(raw.get("minimum"), f"{name}.minimum")
            maximum = _number(raw.get("maximum"), f"{name}.maximum")
            step = _number(raw.get("step"), f"{name}.step")
            default = _number(raw.get("default"), f"{name}.default")
            if not minimum < maximum or step <= 0 or not minimum <= default <= maximum:
                raise ProfileError(f"{name}: require minimum < maximum, step > 0, and bounded default")
            item.update(minimum=minimum, maximum=maximum, step=step, default=default)
        elif "%" in command:
            raise ProfileError(f"{name}: button command cannot contain a parameter placeholder")
        validated.append(item)

    return {
        "profile_name": str(profile.get("profile_name", "VOFA+ Manual Tuning")).strip(),
        "baud": int(profile.get("baud", 115200)),
        "line_ending": line_ending,
        "controls": validated,
    }


def render_setup_sheet(profile: dict) -> str:
    profile = validate_profile(profile)
    ending = r"\r\n" if profile["line_ending"] == "CRLF" else r"\n"
    lines = [
        f"# {profile['profile_name']}",
        "",
        f"- Serial baud: `{profile['baud']}`",
        "- Data engine: `JustFloat`",
        f"- Command line ending: `{ending}`",
        "- Serial owner: `VOFA+ only`",
        "",
        "## VOFA+ controls",
        "",
        "| Name | Widget | Str command | Range / default |",
        "| --- | --- | --- | --- |",
    ]
    for item in profile["controls"]:
        command = item["command"] + ending
        if item["widget"] == "slider":
            settings = (
                f"{item['minimum']:g} to {item['maximum']:g}; "
                f"step {item['step']:g}; default {item['default']:g}"
            )
        else:
            settings = "button"
        lines.append(f"| {item['name']} | {item['widget']} | `{command}` | {settings} |")
    lines.extend(
        [
            "",
            "## Apply in VOFA+",
            "",
            "1. Open the serial device with the baud rate above and select JustFloat.",
            "2. Add every command in Str mode exactly as shown, including the line ending.",
            "3. Add the named slider or button, bind it to the matching command, and copy its limits.",
            "4. Keep an IDLE/STOP button visible and verify device-side bounds before tuning.",
            "5. Save the VOFA+ project after a disconnected, low-energy test succeeds.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", type=Path, help="JSON tuning profile")
    parser.add_argument("--output", type=Path, help="Markdown setup sheet; stdout if omitted")
    args = parser.parse_args()
    profile = json.loads(args.profile.read_text(encoding="utf-8"))
    rendered = render_setup_sheet(profile)
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
