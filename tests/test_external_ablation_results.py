import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "external_ablation" / "results"


class ExternalAblationEvidenceTests(unittest.TestCase):
    def test_cost_matching_gates(self):
        audit = json.loads((RESULTS / "cost_audit.json").read_text(encoding="utf-8"))
        self.assertEqual({row["module"] for row in audit}, {"GAT", "GCN", "GraphSAGE", "MLP+fixed diffusion"})
        self.assertTrue(all(row["parameter_gate"] and row["mac_gate"] for row in audit))

    def test_thirty_paired_seeds_and_holm_result(self):
        with (RESULTS / "matched_replacement_30_seed_results.csv").open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 120)
        self.assertEqual(len({int(row["seed"]) for row in rows}), 30)
        with (RESULTS / "matched_replacement_inference.csv").open(newline="", encoding="utf-8-sig") as handle:
            tests = list(csv.DictReader(handle))
        self.assertEqual(len(tests), 9)
        self.assertGreaterEqual(min(float(row["holm_p_across_9_tests"]) for row in tests), 0.409)

    def test_reproduction_boundaries_are_preserved(self):
        guangzhou = json.loads((RESULTS / "guangzhou_reproduction_check.json").read_text(encoding="utf-8"))
        self.assertFalse(guangzhou["all_reproduced"])
        self.assertEqual(guangzhou["paired_30_seed_results.csv"]["max_absolute_metric_difference"], 0.0)
        jcs = json.loads((RESULTS / "jcs_spot_reproduction.json").read_text(encoding="utf-8"))
        self.assertEqual(jcs["metrics_reproduced_within_tolerance"], 10)
        self.assertEqual(jcs["fronts_reproduced_within_tolerance"], 10)


if __name__ == "__main__":
    unittest.main()
