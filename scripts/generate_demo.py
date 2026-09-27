"""Regenerate the fictional public demo with a fixed seed. No real accounts."""
import csv
import random
from pathlib import Path

from src.engine import FIELDS, SERVICE_LINES, STATES, STAGES

ROOT = Path(__file__).resolve().parents[1]
RNG = random.Random(31082026)
SEGMENTS = ("Regional multispecialty", "Surgical specialty", "Teaching hospital",
            "Quality focused", "Growing mid-sized")
PREFIXES = ("Cedar", "Willow", "Coral", "Silver", "Saffron", "Elm", "Maple",
            "Harbor", "Pine", "River", "Amber", "Orchid")


def generate(count=180):
    rows = []
    for n in range(1, count + 1):
        state = STATES[(n - 1) % len(STATES)]
        segment = SEGMENTS[(n - 1) % len(SEGMENTS)]
        line = SERVICE_LINES[(n - 1) % len(SERVICE_LINES)]
        observed = {key: RNG.choices(range(6), weights=(4, 8, 13, 22, 30, 23))[0]
                    for key in ("expansion", "surgical", "service_fit", "serviceability", "quality", "strategic")}
        if n % 13 == 0:
            observed["expansion"] = ""
        if n % 17 == 0:
            observed["quality"] = ""
        reasons = {
            "expansion_reason": "Hypothetical expansion signal for scenario testing" if observed["expansion"] != "" else "Research needed",
            "surgical_reason": "Synthetic specialty and theatre complexity assumption",
            "service_fit_reason": f"Illustrative {line} match based on segment hypothesis",
            "serviceability_reason": "Assumed travel and delivery capacity by region",
            "quality_reason": "Hypothetical quality initiative for scenario testing" if observed["quality"] != "" else "Research needed",
            "strategic_reason": "Simulated account potential based on segment",
        }
        rows.append({"hospital_id": f"DEMO-{n:04d}",
                     "name": f"{PREFIXES[(n-1)%len(PREFIXES)]} Demo Hospital {n:03d}",
                     "city": f"Demo City {(n-1)%18+1:02d}", "state": state,
                     "segment": segment, "bed_band": RNG.choice(("50-99", "100-199", "200-399", "400+")),
                     "specialty": "Surgical" if segment == "Surgical specialty" else "Multispecialty",
                     "service_line": line, **observed, **reasons,
                     "signal_source_id": "", "quality_source_id": "", "checked_date": "",
                     "verification_status": "Synthetic", "pipeline_stage": STAGES[(n-1)%len(STAGES)]})
    return rows


def main():
    target = ROOT / "public_data" / "hospitals_demo.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(generate())
    print(f"Generated {target} (fictional accounts)")


if __name__ == "__main__":
    main()
