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

    def test_fractional_overrun_is_not_rounded_into_a_pass(self):
        gate = LatencyGate()
        gate.record("stage", 100, 0.0, 100.4)
        self.assertEqual(gate.verdict, Verdict.EXCEEDED_BUDGET)
        self.assertFalse(gate.displayable)
        self.assertEqual(gate.report(), [("stage", 100.4, 100, False)])

    def test_unfinished_stage_cannot_show_as_passing_in_report(self):
        gate = LatencyGate()
        gate.record("stage", 100, 0.0)
        self.assertEqual(gate.verdict, Verdict.INCOMPLETE)
        self.assertEqual(gate.report(), [("stage", None, 100, False)])

    def test_nonfinite_timing_fails_closed(self):
        for start, finish in [
            (float("nan"), 10.0),
            (0.0, float("nan")),
            (float("inf"), float("inf")),
            (0.0, float("inf")),
        ]:
            with self.subTest(start=start, finish=finish):
                gate = LatencyGate()
                gate.record("stage", 100, start, finish)
                self.assertEqual(gate.verdict, Verdict.INCOMPLETE)
                self.assertFalse(gate.report()[0][3])

    def test_invalid_budget_cannot_enable_display(self):
        for budget in (float("nan"), float("inf"), -1):
            with self.subTest(budget=budget):
                gate = LatencyGate()
                gate.record("stage", budget, 0.0, 0.0)
                self.assertEqual(gate.verdict, Verdict.INCOMPLETE)
                self.assertFalse(gate.displayable)

    def test_malformed_or_huge_time_does_not_crash(self):
        for start, finish in [(10**1000, 1), ("bad", 1.0)]:
            with self.subTest(start=start, finish=finish):
                gate = LatencyGate()
                gate.record("stage", 100, start, finish)
                self.assertEqual(gate.verdict, Verdict.INCOMPLETE)
                self.assertFalse(gate.displayable)

    def test_exact_boundary_still_passes(self):
        gate = LatencyGate()
        gate.record("stage", 100, 0.0, 100.0)
        self.assertEqual(gate.verdict, Verdict.WITHIN_BUDGET)
        self.assertTrue(gate.displayable)


if __name__ == "__main__":
    unittest.main()
