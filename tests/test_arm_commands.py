
import sys
import os
import unittest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from arm_commands import format_joint_command, format_action_command


class TestArmCommands(unittest.TestCase):

    def test_valid_joint_command(self):
        self.assertEqual(format_joint_command(2, 90), "2 =90\n")

    def test_minimum_angle(self):
        self.assertEqual(format_joint_command(0, 0), "0 =0\n")

    def test_maximum_angle(self):
        self.assertEqual(format_joint_command(5, 180), "5 =180\n")

    def test_invalid_channel(self):
        with self.assertRaises(ValueError):
            format_joint_command(6, 90)

    def test_invalid_angle(self):
        with self.assertRaises(ValueError):
            format_joint_command(2, 181)

    def test_center_command(self):
        self.assertEqual(format_action_command("c"), "c\n")

    def test_pump_commands(self):
        self.assertEqual(format_action_command("on"), "on\n")
        self.assertEqual(format_action_command("off"), "off\n")

    def test_invalid_action(self):
        with self.assertRaises(ValueError):
            format_action_command("start")


if __name__ == "__main__":
    unittest.main(verbosity=2)
