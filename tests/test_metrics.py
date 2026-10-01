import unittest

from audio_guard import UtteranceMetrics


class MetricTests(unittest.TestCase):
    def test_log_line_contains_only_declared_metadata(self):
        metrics = UtteranceMetrics(
            audio_to_final_ms=1200,
            answer_retrieval_ms=150,
            total_to_display_ms=1400,
            displayable=True,
        )
        line = metrics.as_log_line()
        self.assertIn("audio_to_final_ms=1200", line)
        self.assertNotIn("transcript", line.lower())

    def test_type_has_no_transcript_field(self):
        self.assertNotIn("transcript", UtteranceMetrics.__dataclass_fields__)


if __name__ == "__main__":
    unittest.main()
