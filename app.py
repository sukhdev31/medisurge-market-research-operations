"""Medisurge Market & Operations Intelligence | public synthetic demo."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

from src.engine import (CRITERIA, WEIGHTS, DataError, brief, evidence_flags,
                        load_accounts, load_sources, market_scenario, scored, summary)

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Medisurge | Market Intelligence", page_icon="✳", layout="wide")
st.markdown("""
<style>
  .block-container {padding-top: 1.4rem; max-width: 1500px}
  h1,h2,h3 {color:#15334a;letter-spacing:-.035em}
  .eyebrow {font-size:.7rem;color:#188d96;font-weight:800;letter-spacing:.16em;text-transform:uppercase}
  .hero {background:linear-gradient(115deg,#12304a 0%,#164e64 67%,#157c83 100%);
      border-radius:22px;padding:36px 42px;color:white;margin:8px 0 25px;box-shadow:0 16px 40px #12304a20}
  .hero h1 {color:white;font-size:2.45rem;margin:5px 0 9px}
  .hero p {color:#d7e9ee;max-width:760px;font-size:1.06rem;margin:0}
  .hero .eyebrow {color:#6fe1d4}
  div[data-testid="stMetric"] {background:white;border:1px solid #dde8eb;border-radius:14px;padding:15px 20px}
  div[data-testid="stMetricValue"] {color:#15334a}
  .smallprint {font-size:.84rem;color:#6a7d8c}
  div[data-testid="stSidebar"] {background:#edf4f6}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><div class="eyebrow">Medisurge Inc · Decision workspace</div>'
            '<h1>Where should we focus next?</h1><p>Segment hospital opportunities, inspect the evidence, '
            'test market assumptions, and prepare an account brief your team can challenge.</p></div>',
            unsafe_allow_html=True)
st.warning("PUBLIC DEMO · All hospital accounts, pipeline stages, ratings, and financial inputs are fictional. "
           "No real Medisurge revenue, opportunities, or stakeholder endorsement is claimed.")

with st.sidebar:
    st.markdown("### Decision controls")
    if os.getenv("MEDISURGE_PRIVATE_UPLOAD") == "1":
        upload = st.file_uploader("Load an approved CSV", type="csv", help="Local or access controlled use only. Avoid patient or contact records.")
    else:
        upload = None
        st.caption("Public demo data is fixed. CSV import is disabled unless explicitly enabled in a private environment.")
    if upload:
        try:
            accounts = load_accounts(upload.getvalue())
        except DataError as exc:
            st.error(str(exc))
            st.stop()
        st.warning("Uploaded data is not independently checked by this app. Keep client data private.")
    else:
        accounts = load_accounts(ROOT / "public_data" / "hospitals_demo.csv")
    scenario = st.selectbox("Weight preset", list(WEIGHTS))
    with st.expander("Edit all six weights", expanded=False):
        weights = []
        for criterion, default in zip(CRITERIA, WEIGHTS[scenario]):
            weights.append(st.number_input(criterion.replace("_", " ").title(), 0, 100, default, key=f"w_{scenario}_{criterion}"))
        st.caption(f"Sum: {sum(weights)} / 100")
        if sum(weights) != 100:
            st.error("Weights must total 100. Adjust the six values to continue.")
            st.stop()
    weights = tuple(weights)
    states = st.multiselect("Geographies", sorted({a.state for a in accounts}), default=sorted({a.state for a in accounts}))
    lines = st.multiselect("Services", sorted({a.service_line for a in accounts}), default=sorted({a.service_line for a in accounts}))
    st.caption("Scores express a transparent hypothesis. Human review owns final priority.")

sources = load_sources(ROOT / "public_data" / "source_register.csv")
filtered = [a for a in accounts if a.state in states and a.service_line in lines]
rows = scored(filtered, weights, sources)
stats = summary(filtered, weights, sources) if filtered else None

def count_chart(counts):
    st.bar_chart(pd.DataFrame([{"Group": k, "Accounts": v} for k,v in counts.items()]),
                 x="Group", y="Accounts", horizontal=True)
overview, priorities, market, evidence, guide = st.tabs(
    ["Overview", "Account priorities", "Market scenarios", "Evidence & briefs", "How to use"])

with overview:
    st.subheader("Opportunity overview")
    if not stats:
        st.info("Choose at least one geography and service line.")
    else:
        a,b,c,d = st.columns(4)
        a.metric("Accounts in view", stats["accounts"])
        b.metric("Scenario high priority", stats["high"])
        c.metric("Research first", stats["research_first"])
        d.metric("Selected geographies", len(stats["geographies"]))
        left,right = st.columns(2)
        with left:
            st.markdown("#### Segments")
            count_chart(stats["segments"])
            st.markdown("#### Service fit")
            count_chart(stats["services"])
        with right:
            st.markdown("#### Geography")
            count_chart(stats["geographies"])
            st.markdown("#### Simulated pipeline")
            from collections import Counter
            count_chart(dict(Counter(a.pipeline_stage for a in filtered)))
        st.caption("Account count reflects only the loaded example or uploaded set. It is not a count of real target hospitals.")

with priorities:
    st.subheader("Account ranking")
    st.caption("The score floor excludes missing factors. The ceiling assumes missing factors could score 5/5. "
               "Coverage measures completeness of ratings, not independent verification.")
    st.dataframe([{k: r[k] for k in ("hospital_id","name","state","segment","service_line",
                   "score_floor","score_ceiling","evidence_coverage","priority","verification_status")}
                   for r in rows], width="stretch", hide_index=True)
    if rows:
        st.markdown("#### Why this account ranks here")
        selected = st.selectbox("Inspect account", rows, format_func=lambda r: f'{r["name"]} · {r["score_floor"]:.1f}/100')
        for key, weight in zip(CRITERIA, weights):
            raw = selected[key]
            st.write(f"**{key.replace('_',' ').title()} ({weight}%):** "
                     f"{'Unknown' if raw is None else str(raw)+'/5'} · {selected[key+'_reason']}")
        st.info("Proposed next step: research the exact hospital entity, then validate fit with Medisurge management.")
        output = json.dumps({"scenario": scenario, "weights": dict(zip(CRITERIA, weights)),
                             "accounts": [{k: r[k] for k in ("hospital_id","score_floor","score_ceiling",
                                          "evidence_coverage","priority")} for r in rows]}, indent=2)
        st.download_button("Download scenario JSON", output, "medisurge_scenario.json", "application/json")

with market:
    st.subheader("Bottom-up sizing · hypothetical inputs")
    st.caption("TAM = applicable accounts × project value. SAM applies serviceability. "
               "SOM caps assumed capture by annual delivery capacity. Counts may be fractional expected values.")
    p,q,r = st.columns(3)
    with p:
        universe = st.number_input("Eligible geography account universe (assumed)", 0, 100000, 1200, 10)
        applicable = st.slider("Service applicability", 0, 100, 45) / 100
    with q:
        coverage = st.slider("Serviceable share", 0, 100, 35) / 100
        value = st.number_input("Illustrative average project value (₹ lakh)", 0.0, 10000.0, 12.0, 1.0)
    with r:
        capture = st.slider("Possible capture over 12 months", 0, 100, 8) / 100
        capacity = st.number_input("Annual project capacity", 0, 10000, 14, 1)
    result = market_scenario(universe, applicable, coverage, value, capture, capacity)
    x,y,z = st.columns(3)
    x.metric("TAM · scenario", f'₹{result["tam_lakh"]:,.0f} lakh')
    y.metric("SAM · scenario", f'₹{result["sam_lakh"]:,.0f} lakh')
    z.metric("SOM · scenario", f'₹{result["som_lakh"]:,.0f} lakh')
    st.write(f'Expected applicable accounts **{result["eligible"]:,.1f}**, serviceable **{result["serviceable"]:,.1f}**, '
             f'captured **{result["captured"]:,.1f}**. Capacity limit: **{"binding" if result["capacity_bound"] else "not binding"}**.')
    st.markdown("#### Sensitivity to value and serviceability")
    variants = []
    for label, mult in (("Low", .7), ("Base", 1.0), ("High", 1.3)):
        case = market_scenario(universe, applicable, min(1,coverage*mult),value*mult,capture,capacity)
        variants.append({"Case": label, "Serviceable %": round(min(1,coverage*mult)*100,1),
                         "Value ₹ lakh": round(value*mult,1), "SAM ₹ lakh": round(case["sam_lakh"]),
                         "SOM ₹ lakh": round(case["som_lakh"])})
    st.dataframe(variants, hide_index=True, width="stretch")
    st.caption("These are editable forecasts of a hypothetical market, not observed Medisurge sales or a verified market estimate.")

with evidence:
    st.subheader("Evidence quality and account brief")
    if not rows:
        st.info("Choose an account in the sidebar filters.")
    else:
        item = st.selectbox("Account", filtered, format_func=lambda a: f"{a.name} ({a.hospital_id})", key="brief_acct")
        report = brief(item, weights, sources)
        flags = evidence_flags(item, set(sources))
        st.metric("Evidence issues", len(flags))
        st.write("**Verified facts**")
        if not report["facts"]:
            st.info("No human-verified source claims exist for this fictional account.")
        for fact in report["facts"]:
            st.write(f'{fact["claim"]} · [{fact["source_id"]}]({fact["url"]}) · checked {fact["checked_date"]}')
        st.write("**Potential service fit · inference**")
        st.write(report["inferences"][0])
        st.write("**Missing evidence**")
        for gap in report["research_gaps"]:
            st.write("•", gap)
        st.write("**Suggested next action**", report["next_action"])
        st.download_button("Download accountable brief (JSON)", json.dumps(report, indent=2),
                           f'{item.hospital_id}_brief.json', "application/json")
    st.caption("Brief generation is deterministic and source constrained. An LLM is not used or claimed in this public demo.")

with guide:
    st.subheader("From portfolio demo to a business decision")
    st.markdown("""
1. Identify the decision owner and confirm serviceable geography and service lines.
2. Resolve each real hospital identity against its official site. Add atomic claims and URLs to the source register.
3. Review ratings and reasons with a Medisurge stakeholder. Label facts, inferences, and assumptions.
4. Vary the weights and financial inputs. Check if the top ten accounts change materially.
5. Record feedback and actual time saved before making any claim about business impact.

**Safety:** This public deployment is an illustrative analytical viewer with CSV upload disabled. The included dataset
contains no real hospital, lead, or contact record. For confidential Medisurge data,
use an access-controlled private deployment with persistence, security review, and approval from the data owner.
""")
