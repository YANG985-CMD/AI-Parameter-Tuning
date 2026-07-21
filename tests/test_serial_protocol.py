import math
import struct
import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).parents[1] / "skills" / "ai-parameter-tuning" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from serial_protocol import JustFloatParser, ProtocolError, TAIL, build_command


class SerialProtocolTest(unittest.TestCase):
    def test_fragmented_frame(self):
        parser = JustFloatParser(["version", "value"], version=1.0)
        packet = struct.pack("<2f", 1.0, 2.5) + TAIL
        self.assertEqual(parser.feed(packet[:5]), [])
        self.assertEqual(parser.feed(packet[5:]), [{"version": 1.0, "value": 2.5}])

    def test_noise_and_wrong_version_are_rejected(self):
        parser = JustFloatParser(["version", "value"], version=1.0)
        bad = b"noise" + struct.pack("<2f", 2.0, 3.0) + TAIL
        good = struct.pack("<2f", 1.0, 4.0) + TAIL
        self.assertEqual(parser.feed(bad + good), [{"version": 1.0, "value": 4.0}])

    def test_nonfinite_frame_is_rejected(self):
        parser = JustFloatParser(["version", "value"], version=1.0)
        self.assertEqual(parser.feed(struct.pack("<2f", 1.0, math.nan) + TAIL), [])

    def test_bounded_command(self):
        self.assertEqual(build_command("apidh", [5, 0.2]), b"APIDH 5 0.2\r\n")

    def test_unknown_and_out_of_range_commands_fail(self):
        with self.assertRaises(ProtocolError):
            build_command("PWM", [100, 100, 100, 100])
        with self.assertRaises(ProtocolError):
            build_command("APIDH", [50, 0])

    def test_idle_has_no_arguments(self):
        self.assertEqual(build_command("idle"), b"IDLE\r\n")
        with self.assertRaises(ProtocolError):
            build_command("IDLE", [1])


if __name__ == "__main__":
    unittest.main()
