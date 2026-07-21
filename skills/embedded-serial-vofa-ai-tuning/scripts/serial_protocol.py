#!/usr/bin/env python3
"""Reusable JustFloat parser and bounded ASCII command builder."""

from __future__ import annotations

import argparse
import json
import math
import struct
from dataclasses import dataclass
from typing import Iterable

TAIL = b"\x00\x00\x80\x7f"


class ProtocolError(ValueError):
    pass


class JustFloatParser:
    def __init__(self, channel_names: Iterable[str], version: float | None = None):
        self.channel_names = tuple(channel_names)
        if not self.channel_names or len(set(self.channel_names)) != len(self.channel_names):
            raise ProtocolError("channel names must be non-empty and unique")
        self.payload_size = 4 * len(self.channel_names)
        self.version = version
        self.buffer = bytearray()

    def feed(self, data: bytes) -> list[dict[str, float]]:
        self.buffer.extend(data)
        frames = []
        while True:
            tail_index = self.buffer.find(TAIL)
            if tail_index < 0:
                self._trim_noise()
                break
            if tail_index < self.payload_size:
                del self.buffer[: tail_index + len(TAIL)]
                continue
            start = tail_index - self.payload_size
            payload = bytes(self.buffer[start:tail_index])
            del self.buffer[: tail_index + len(TAIL)]
            values = struct.unpack(f"<{len(self.channel_names)}f", payload)
            if not all(math.isfinite(value) for value in values):
                continue
            if self.version is not None and not math.isclose(values[0], self.version, abs_tol=1e-4):
                continue
            frames.append(dict(zip(self.channel_names, values)))
        return frames

    def _trim_noise(self) -> None:
        maximum = self.payload_size + len(TAIL) - 1
        if len(self.buffer) > maximum:
            del self.buffer[:-maximum]


@dataclass(frozen=True)
class CommandSpec:
    minimums: tuple[float, ...]
    maximums: tuple[float, ...]


DEFAULT_POLICY = {
    "APIDH": CommandSpec((0.1, 0.0), (40.0, 10.0)),
    "APIDK": CommandSpec((0.1, 0.0), (40.0, 10.0)),
    "ASLEW": CommandSpec((5.0,), (120.0,)),
    "AVFF": CommandSpec((-50.0, -50.0), (50.0, 50.0)),
    "APFF": CommandSpec((0.0, 0.0), (15.0, 15.0)),
    "APFFD": CommandSpec((0.0, 0.0, 0.0, 0.0), (15.0, 15.0, 15.0, 15.0)),
    "PAMS": CommandSpec((0.0, 0.0, 0.0), (1.0, 2.0, 5.0)),
    "TRIAL": CommandSpec((0.0,), (16777215.0,)),
    "ETEL": CommandSpec((0.0,), (6.0,)),
}
NO_ARGUMENT_COMMANDS = {"IDLE", "STOP", "STREAM", "RESET", "ZERO"}


def build_command(name: str, values: Iterable[float] = (), policy=None) -> bytes:
    policy = DEFAULT_POLICY if policy is None else policy
    command = name.strip().upper()
    numbers = tuple(float(value) for value in values)
    if command in NO_ARGUMENT_COMMANDS:
        if numbers:
            raise ProtocolError(f"{command} takes no arguments")
    elif command in policy:
        spec = policy[command]
        if len(numbers) != len(spec.minimums):
            raise ProtocolError(f"{command} requires {len(spec.minimums)} arguments")
        for index, (value, low, high) in enumerate(zip(numbers, spec.minimums, spec.maximums), 1):
            if not math.isfinite(value) or not low <= value <= high:
                raise ProtocolError(f"{command} argument {index} must be finite and in [{low}, {high}]")
    else:
        raise ProtocolError(f"command is not allowlisted: {command}")
    suffix = "" if not numbers else " " + " ".join(format(value, ".9g") for value in numbers)
    return f"{command}{suffix}\r\n".encode("ascii")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", help="allowlisted command name")
    parser.add_argument("values", nargs="*", type=float)
    parser.add_argument("--json", action="store_true", help="print a JSON dry-run record")
    args = parser.parse_args()
    wire = build_command(args.command, args.values)
    if args.json:
        print(json.dumps({"dry_run": True, "wire_ascii": wire.decode("ascii").rstrip()}))
    else:
        print(wire.decode("ascii"), end="")


if __name__ == "__main__":
    main()
