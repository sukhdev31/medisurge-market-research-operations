"""Pure, auditable logic shared by dashboard, CLI, and tests.

This demonstration operates only on explicitly synthetic account data.
All market values and capacity inputs are hypothetical scenario inputs.
"""
from __future__ import annotations

import csv
import io
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

SERVICE_LINES = ("CSSD consultancy", "NABH readiness", "Modular OT")
CRITERIA = ("expansion", "surgical", "service_fit", "serviceability", "quality", "strategic")
WEIGHTS = {
    "Balanced": (25, 20, 15, 15, 10, 15),
    "Expansion led": (35, 20, 15, 10, 10, 10),
    "Serviceability led": (15, 15, 15, 30, 10, 15),
}
FIELDS = ("hospital_id", "name", "city", "state", "segment", "bed_band", "specialty",
          "service_line", "expansion", "surgical", "service_fit", "serviceability",
          "quality", "strategic", "expansion_reason", "surgical_reason", "service_fit_reason",
          "serviceability_reason", "quality_reason", "strategic_reason", "signal_source_id",
          "quality_source_id", "checked_date", "verification_status", "pipeline_stage")
STATES = ("Punjab", "Haryana", "Himachal Pradesh", "Chandigarh", "Rajasthan", "Delhi")
STAGES = ("Unresearched", "Researching", "Qualified", "Contact planned")


class DataError(ValueError):
    pass


@dataclass(frozen=True)
class Account:
    hospital_id: str
    name: str
    city: str
    state: str
    segment: str
    bed_band: str
    specialty: str
    service_line: str
    expansion: int | None
    surgical: int | None
    service_fit: int | None
    serviceability: int | None
    quality: int | None
    strategic: int | None
    expansion_reason: str
    surgical_reason: str
    service_fit_reason: str
    serviceability_reason: str
    quality_reason: str
    strategic_reason: str
    signal_source_id: str
    quality_source_id: str
    checked_date: str
    verification_status: str
    pipeline_stage: str


def load_accounts(data: bytes | str | Path) -> list[Account]:
    """Validate exact schema and value ranges; never interpret CSV as executable code."""
    if isinstance(data, Path):
        raw = data.read_bytes()
    elif isinstance(data, str):
        raw = data.encode("utf-8")
    else:
        raw = data
    if len(raw) > 5_000_000:
        raise DataError("CSV exceeds the 5 MB demo limit.")
    try:
        stream = io.StringIO(raw.decode("utf-8-sig"), newline="")
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or tuple(reader.fieldnames) != FIELDS:
            raise DataError("CSV columns must exactly match public_data/hospitals_demo.csv.")
        accounts: list[Account] = []
        seen: set[str] = set()
        for index, row in enumerate(reader, 2):
            if index > 10_001:
                raise DataError("CSV exceeds 10,000 accounts.")
            if None in row or any(value is None for value in row.values()):
                raise DataError(f"Row {index}: wrong number of cells.")
            values = {key: value.strip() for key, value in row.items()}
            if not values["hospital_id"] or values["hospital_id"] in seen:
                raise DataError(f"Row {index}: missing or duplicate hospital_id.")
            seen.add(values["hospital_id"])
            for key in ("name", "city", "state", "segment", "service_line"):
                if not values[key] or len(values[key]) > 160:
                    raise DataError(f"Row {index}: {key} is empty or too long.")
            if values["service_line"] not in SERVICE_LINES:
                raise DataError(f"Row {index}: unknown service line.")
            if values["pipeline_stage"] not in STAGES:
                raise DataError(f"Row {index}: unknown pipeline stage.")
            for key in CRITERIA:
                v = values[key]
                if v == "":
                    values[key] = None
                else:
                    try:
                        n = int(v)
                    except ValueError as exc:
                        raise DataError(f"Row {index}: {key} must be 0-5 or blank.") from exc
                    if n not in range(6):
                        raise DataError(f"Row {index}: {key} must be 0-5 or blank.")
                    values[key] = n
                if values[key] is not None and not values[f"{key}_reason"]:
                    raise DataError(f"Row {index}: {key} needs a reason.")
            if values["signal_source_id"] and values["expansion"] is None:
                raise DataError(f"Row {index}: signal source has no expansion score.")
            if values["quality_source_id"] and values["quality"] is None:
                raise DataError(f"Row {index}: quality source has no quality score.")
            if values["verification_status"] not in ("Synthetic", "Verified", "Unverified"):
                raise DataError(f"Row {index}: invalid verification status.")
            if values["verification_status"] == "Verified" and not values["checked_date"]:
                raise DataError(f"Row {index}: verified record needs a date.")
            if values["checked_date"]:
                try:
                    date.fromisoformat(values["checked_date"])
                except ValueError as exc:
                    raise DataError(f"Row {index}: date must be YYYY-MM-DD.") from exc
            accounts.append(Account(**values))
        if not accounts:
            raise DataError("CSV has no accounts.")
        return accounts
    except UnicodeDecodeError as exc:
        raise DataError("CSV must use UTF-8.") from exc


def score_account(account: Account, weights: tuple[int, ...],
                  sources: dict[str, dict] | None = None) -> dict:
    if len(weights) != 6 or any(w < 0 for w in weights) or sum(weights) != 100:
        raise ValueError("Weights must be six nonnegative percentages totaling 100.")
    observed = [getattr(account, criterion) for criterion in CRITERIA]
    # Missing factors remain unknown. The lower-bound score does not assert absence of need.
    lower_bound = sum(w * value / 5 for w, value in zip(weights, observed) if value is not None)
    missing_weight = sum(w for w, value in zip(weights, observed) if value is None)
    confidence = 100 - missing_weight
    approved_sources = sources or {}
    def usable(sid: str) -> bool:
        source = approved_sources.get(sid, {})
        return (bool(sid) and source.get("verified_by_human") == "Yes" and
                source.get("entity_name", "").casefold() == account.name.casefold() and
                urlparse(source.get("source_url", "")).scheme == "https" and
                bool(source.get("claim")) and recent(source.get("checked_date", "")))
    needs_research = (confidence < 80 or account.verification_status == "Unverified" or
                      (account.verification_status == "Verified" and
                       (not recent(account.checked_date) or
                        (account.expansion is not None and not usable(account.signal_source_id)) or
                        (account.quality is not None and not usable(account.quality_source_id)))))
    return {"score_floor": round(lower_bound, 1), "score_ceiling": round(lower_bound + missing_weight, 1),
            "evidence_coverage": confidence,
            "priority": "Research first" if needs_research else "High" if lower_bound >= 72 else "Medium" if lower_bound >= 52 else "Low"}


def scored(accounts: Iterable[Account], weights: tuple[int, ...],
           sources: dict[str, dict] | None = None) -> list[dict]:
    rows = [{**vars(a), **score_account(a, weights, sources)} for a in accounts]
    return sorted(rows, key=lambda r: (r["priority"] == "Research first", -r["score_floor"], r["hospital_id"]))


def market_scenario(universe: int, applicable_share: float, serviceable_share: float,
                    project_value_lakh: float, capture_share: float, annual_capacity: int) -> dict:
    if universe < 0 or annual_capacity < 0 or project_value_lakh < 0 or not all(
        0 <= x <= 1 for x in (applicable_share, serviceable_share, capture_share)
    ):
        raise ValueError("Use nonnegative counts/value and shares in [0, 1].")
    eligible = universe * applicable_share
    serviceable = eligible * serviceable_share
    captured = min(serviceable * capture_share, annual_capacity)
    return {"eligible": eligible, "serviceable": serviceable, "captured": captured,
            "tam_lakh": eligible * project_value_lakh,
            "sam_lakh": serviceable * project_value_lakh,
            "som_lakh": captured * project_value_lakh,
            "capacity_bound": serviceable * capture_share > annual_capacity}


def evidence_flags(account: Account, known_sources: set[str], today: date | None = None) -> list[str]:
    today = today or date.today()
    flags = []
    if account.verification_status != "Verified":
        flags.append("Account facts are not independently verified")
    if not account.checked_date:
        flags.append("Missing verification date")
    else:
        age = (today - date.fromisoformat(account.checked_date)).days
        if age > 365:
            flags.append("Verification older than 12 months")
        if age < 0:
            flags.append("Verification date is in the future")
    for key in ("signal_source_id", "quality_source_id"):
        sid = getattr(account, key)
        if sid and sid not in known_sources:
            flags.append(f"Unknown source ID: {sid}")
    if account.expansion is not None and not account.signal_source_id:
        flags.append("Expansion rating has no source ID")
    if account.quality is not None and not account.quality_source_id:
        flags.append("Quality rating has no source ID")
    return flags


def recent(value: str, today: date | None = None) -> bool:
    try:
        age = ((today or date.today()) - date.fromisoformat(value)).days
    except ValueError:
        return False
    return 0 <= age <= 365


def brief(account: Account, weights: tuple[int, ...], source_claims: dict[str, dict]) -> dict:
    """Grounded, deterministic brief. No unsupported factual inference is promoted to fact."""
    result = score_account(account, weights, source_claims)
    facts = []
    for sid in (account.signal_source_id, account.quality_source_id):
        source = source_claims.get(sid)
        if (sid and source and source.get("verified_by_human") == "Yes" and
                source.get("entity_name", "").casefold() == account.name.casefold() and
                urlparse(source.get("source_url", "")).scheme == "https" and
                recent(source.get("checked_date", ""))):
            facts.append({"claim": source["claim"], "source_id": sid,
                          "url": source["source_url"], "checked_date": source["checked_date"]})
    gaps = evidence_flags(account, set(source_claims))
    gaps += [f"Missing {key.replace('_', ' ')} rating" for key in CRITERIA if getattr(account, key) is None]
    if not facts:
        gaps.append("No independently verified source claims supplied for this account")
    return {"entity": f"{account.name} ({account.city}, {account.state})", "facts": facts,
            "inferences": [f"Possible {account.service_line} fit: {account.service_fit_reason}. Human validation required."],
            "assumptions": ["Scores and commercial scenario are editable hypotheses, not a purchase forecast."],
            "research_gaps": list(dict.fromkeys(gaps)), "score": result,
            "next_action": "Verify entity and source claims before outreach" if gaps else "Review with business owner before outreach"}


def load_sources(path: Path) -> dict[str, dict]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        result = {}
        for row in reader:
            sid = row["source_id"].strip()
            if not sid or sid in result:
                raise DataError("Duplicate or empty source ID")
            if row.get("verified_by_human") not in ("Yes", "No"):
                raise DataError(f"Source {sid}: verification must be Yes or No")
            if not row.get("claim") or not row.get("entity_name") or not row.get("source_url"):
                raise DataError(f"Source {sid}: entity, claim and URL are required")
            if urlparse(row["source_url"]).scheme != "https":
                raise DataError(f"Source {sid}: URL must use https")
            try:
                date.fromisoformat(row.get("checked_date", ""))
            except ValueError as exc:
                raise DataError(f"Source {sid}: checked date must be YYYY-MM-DD") from exc
            result[sid] = row
        return result


def summary(accounts: list[Account], weights: tuple[int, ...],
            sources: dict[str, dict] | None = None) -> dict:
    rows = scored(accounts, weights, sources)
    return {"accounts": len(rows), "high": sum(r["priority"] == "High" for r in rows),
            "research_first": sum(r["priority"] == "Research first" for r in rows),
            "segments": dict(Counter(a.segment for a in accounts)),
            "geographies": dict(Counter(a.state for a in accounts)),
            "services": dict(Counter(a.service_line for a in accounts))}
