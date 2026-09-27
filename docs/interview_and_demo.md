# Presenter notes and interview defence

## 30-second opening

“Medisurge serves healthcare operations around CSSD, sterilisation and NABH readiness. I built a decision prototype to make hospital account research more consistent. It lets a business owner see the source and reason behind a priority score, change assumptions and spot missing evidence before outreach. The public portfolio version uses fictional accounts, so I present its metrics as scenarios rather than company outcomes.”

## Five-minute walkthrough

1. State the decision and the three illustrative service lines. Show the Overview's 180-account demo and filter a geography.
2. In Account priorities, point to the six weights, change a preset, inspect an account's reasons and score range.
3. In Market scenarios, explain the bottom-up arithmetic and the 14-project capacity cap.
4. In Evidence & briefs, explain why no real claims appear for a fictional entity and why the suggested action is verification.
5. Finish with the decision memo's 30/60/90-day plan and the specific missing validation: an owner interview, 25 verified accounts and measured preparation time.

## What you built and can defend

- Deterministic 180-row data generator with fixed seed and clearly fictional identifiers.
- CSV schema and value validation, bounded upload size, six criterion scoring and missing-value interval.
- Three editable weighting presets, source ID and exact-entity checks, source recency guardrail and separated fact/inference brief.
- Bottom-up TAM/SAM/SOM scenario with capacity cap, an Excel formula model and a deck.
- Tests for maths, invalid input, evidence rejection and privacy-aware release packaging.

## Questions likely to come up

**Is ₹168 lakh real revenue?** No. It is a model output from assumed account count, project value and a 14-project cap. Medisurge has not supplied approved price or capacity inputs here.

**Why rank an account without an official source?** The public accounts are explicitly fictional demonstrations of the score mechanics. A real unverified account routes to research; the brief does not promote unverified claims to fact.

**Why these weights?** They are hypotheses from the earlier P2 charter. The owner needs to review them, and a sensitivity test should examine rank changes before use.

**Did you use AI?** The public release uses deterministic source constrained brief generation, without an LLM API. A model assisted version remains conditional on a verified corpus and a frozen evaluation set.

**Where is Power BI?** The live dashboard is Streamlit. The repo has an editable Excel workbook and SQL schema. No `.pbix` file has been built, so do not claim one.

**What would make this production ready for Medisurge?** Confirm business criteria and data permissions, research verified hospital and competitor evidence, then add private authentication, persistent audit records and an operating owner. The public prototype is ready to deploy for a portfolio demo; it is not an approved private CRM.

## Honest resume bullet after publishing

“Built a deployable hospital opportunity intelligence prototype for Medisurge with 180 synthetic accounts, six auditable scoring factors, source checks, an editable TAM/SAM/SOM model, an Excel decision workbook and eight automated tests.”

Add a live URL only after actual deployment, and replace the synthetic metrics with observed business impact only after a measured pilot.
