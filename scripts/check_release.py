"""Fail on public-tree secrets, real-looking account names, or missing deliverables."""
from pathlib import Path
from src.engine import WEIGHTS, load_accounts, scored

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ("README.md", "app.py", "requirements.txt", "public_data/hospitals_demo.csv",
            "excel/medisurge_market_model.xlsx", "docs/Medisurge_Opportunity_Review_v2.pptx",
            "docs/recommendation.md", "sql/schema.sql")
for rel in REQUIRED:
    assert (ROOT / rel).is_file(), f"Missing: {rel}"
for forbidden in (".env", ".streamlit/secrets.toml", "private_working"):
    assert not (ROOT / forbidden).exists(), f"Remove private path: {forbidden}"
accounts = load_accounts(ROOT / "public_data/hospitals_demo.csv")
assert all(a.verification_status == "Synthetic" and "Demo Hospital" in a.name for a in accounts)
assert all(sum(w)==100 for w in WEIGHTS.values())
assert len(scored(accounts, WEIGHTS["Balanced"]))==len(accounts)
print(f"PASS: {len(accounts)} fictional accounts; required files and public boundary present")
