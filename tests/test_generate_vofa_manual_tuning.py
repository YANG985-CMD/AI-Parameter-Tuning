import json
import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).parents[1] / "skills" / "ai-parameter-tuning" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from generate_vofa_manual_tuning import ProfileError, render_setup_sheet, validate_profile


class VofaManualTuningTest(unittest.TestCase):
    def setUp(self):
        self.profile = {
            "profile_name": "Test PID",
            "baud": 115200,
            "line_ending": "CRLF",
            "controls": [
                {
                    "name": "Kp",
                    "widget": "slider",
                    "command": "PID_KP %f",
                    "minimum": 0,
                    "maximum": 10,
                    "step": 0.1,
                    "default": 1,
                },
                {"name": "Stop", "widget": "button", "command": "IDLE"},
            ],
        }

    def test_render_contains_concrete_vofa_settings(self):
        output = render_setup_sheet(self.profile)
        self.assertIn("`PID_KP %f\\r\\n`", output)
        self.assertIn("0 to 10; step 0.1; default 1", output)
        self.assertIn("`IDLE\\r\\n`", output)

    def test_slider_requires_one_placeholder(self):
        self.profile["controls"][0]["command"] = "PID_KP"
        with self.assertRaises(ProfileError):
            validate_profile(self.profile)

    def test_invalid_bounds_fail(self):
        self.profile["controls"][0]["maximum"] = 0
        with self.assertRaises(ProfileError):
            validate_profile(self.profile)

    def test_button_cannot_have_placeholder(self):
        self.profile["controls"][1]["command"] = "IDLE %f"
        with self.assertRaises(ProfileError):
            validate_profile(self.profile)


if __name__ == "__main__":
    unittest.main()
