import csv
import tempfile
import unittest
from pathlib import Path

from xai_facility_location.workflow import load_cells, planner_rerun, smoke_result, synthetic_cells


class ReferenceHarnessTests(unittest.TestCase):
    def test_smoke_is_deterministic_and_enforces_exclusion(self):
        first = smoke_result(2026)
        second = smoke_result(2026)
        self.assertEqual(first, second)
        excluded = set(first["planner_excluded_ids"])
        revised = set(first["revised_plan"]["selected_ids"])
        self.assertTrue(excluded.isdisjoint(revised))

    def test_planner_rerun_keeps_budget(self):
        cells = synthetic_cells(7, side=6)
        result = planner_rerun(cells, 3, 2.0, 1.0, ["synthetic_00_00"])
        self.assertEqual(len(result["initial_plan"]["selected_ids"]), 3)
        self.assertEqual(len(result["revised_plan"]["selected_ids"]), 3)

    def test_csv_contract(self):
        rows = [
            {"cell_id": "a", "x_km": 0, "y_km": 0, "demand": 10, "hazard": 0.1, "feasible": "true"},
            {"cell_id": "b", "x_km": 1, "y_km": 0, "demand": 20, "hazard": 0.2, "feasible": "false"},
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cells.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
            cells = load_cells(path)
        self.assertEqual([cell.cell_id for cell in cells], ["a", "b"])
        self.assertTrue(cells[0].feasible)
        self.assertFalse(cells[1].feasible)


if __name__ == "__main__":
    unittest.main()

