import unittest

from audio_guard import LatencyGate, Verdict


class LatencyTests(unittest.TestCase):
    def test_empty_gate_is_incomplete(self):
        self.assertEqual(LatencyGate().verdict, Verdict.INCOMPLETE)

    def test_unfinished_stage_is_incomplete(self):
        gate = LatencyGate()
        gate.record("transcribe", 1000, 0)
        self.assertEqual(gate.verdict, Verdict.INCOMPLETE)

    def test_over_budget_suppresses_display(self):
        gate = LatencyGate()
        gate.record("transcribe", 1000, 0, 1200)
        self.assertEqual(gate.verdict, Verdict.EXCEEDED_BUDGET)
        self.assertFalse(gate.displayable)

    def test_all_stages_within_budget_display(self):
        gate = LatencyGate()
        gate.record("transcribe", 1500, 0, 1200)
        gate.record("retrieve", 500, 1200, 1400)
        self.assertTrue(gate.displayable)


if __name__ == "__main__":
    unittest.main()
