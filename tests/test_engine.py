import csv
import io
import unittest
from dataclasses import replace
from datetime import date
from pathlib import Path

from src.engine import (FIELDS, WEIGHTS, DataError, brief, evidence_flags,
                        load_accounts, market_scenario, score_account, scored)

ROOT = Path(__file__).resolve().parents[1]


class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accounts = load_accounts(ROOT / "public_data" / "hospitals_demo.csv")

    def test_demo_is_fictional_and_deterministic(self):
        self.assertEqual(len(self.accounts), 180)
        self.assertEqual(len({a.hospital_id for a in self.accounts}), 180)
        self.assertTrue(all(a.verification_status == "Synthetic" and "Demo" in a.name for a in self.accounts))

    def test_score_bounds_and_ranking(self):
        for preset in WEIGHTS.values():
            rows = scored(self.accounts, preset)
            self.assertEqual(len(rows), 180)
            for r in rows:
                self.assertLessEqual(r["score_floor"], r["score_ceiling"])
                self.assertLessEqual(r["score_ceiling"], 100)
            self.assertTrue(all(r["score_floor"] >= rows[10]["score_floor"] for r in rows[:10]
                                if r["priority"] != "Research first"))

    def test_missing_factors_are_a_range_and_low_coverage_routes_to_research(self):
        a = replace(self.accounts[0], expansion=None, quality=None, service_fit=None)
        result = score_account(a, WEIGHTS["Balanced"])
        self.assertEqual(result["priority"], "Research first")
        self.assertEqual(result["score_ceiling"]-result["score_floor"], 50)

    def test_verified_but_unsourced_signal_routes_to_research(self):
        a = replace(self.accounts[0], verification_status="Verified", checked_date="2026-09-01")
        self.assertEqual(score_account(a, WEIGHTS["Balanced"])["priority"], "Research first")
        self.assertIn("Expansion rating has no source ID", evidence_flags(a, set(), date(2026,9,25)))

    def test_tam_sam_som_capacity_binding(self):
        x = market_scenario(1200, .45, .35, 12, .08, 14)
        self.assertAlmostEqual(x["tam_lakh"], 6480)
        self.assertAlmostEqual(x["sam_lakh"], 2268)
        self.assertAlmostEqual(x["som_lakh"], 168)
        self.assertTrue(x["capacity_bound"])
        self.assertLessEqual(x["som_lakh"], x["sam_lakh"])

    def test_market_inputs_rejected(self):
        with self.assertRaises(ValueError):
            market_scenario(10, 1.2, .5, 10, .1, 5)

    def test_evidence_brief_does_not_repeat_unverified_claims(self):
        account = replace(self.accounts[0], signal_source_id="SRC-1")
        sources = {"SRC-1": {"entity_name":account.name,"claim":"A new theatre is planned", "source_url":"https://example.org",
                             "checked_date":date.today().isoformat(), "verified_by_human":"No"}}
        self.assertEqual(brief(account, WEIGHTS["Balanced"], sources)["facts"], [])
        sources["SRC-1"]["verified_by_human"] = "Yes"
        b = brief(account, WEIGHTS["Balanced"], sources)
        self.assertEqual(b["facts"][0]["source_id"], "SRC-1")
        sources["SRC-1"]["entity_name"] = "Another Demo Hospital"
        self.assertEqual(brief(account, WEIGHTS["Balanced"], sources)["facts"], [])

    def test_csv_injection_columns_and_duplicates_rejected(self):
        with (ROOT / "public_data" / "hospitals_demo.csv").open(encoding="utf-8",newline="") as h:
            row = next(csv.DictReader(h))
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=FIELDS)
        writer.writeheader(); writer.writerow(row); writer.writerow(row)
        with self.assertRaisesRegex(DataError, "duplicate"):
            load_accounts(output.getvalue())
        row["expansion"] = "__import__('os').system('bad')"
        output = io.StringIO(); writer = csv.DictWriter(output, fieldnames=FIELDS)
        writer.writeheader(); writer.writerow(row)
        with self.assertRaisesRegex(DataError, "0-5"):
            load_accounts(output.getvalue())


if __name__ == "__main__":
    unittest.main()
