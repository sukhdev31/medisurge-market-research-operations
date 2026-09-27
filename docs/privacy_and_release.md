# Public release and private implementation

## Public demo

180 generated fictional account names, simulated ratings and pipeline stages, editable hypothetical commercial inputs. No external hospital facts, existing client relationships, contacts or prices. The dataset and deck can be shared publicly with their scenario labels.

## Production boundary

This is a deployable public **decision prototype** with CSV upload disabled, not an approved production CRM for sensitive hospital data. A local, explicitly enabled CSV import is available for approved testing only. An actual Medisurge rollout needs stakeholder-approved criteria, real public fact verification, access control and audit logging, a private data store, retention policy, backups, and consent for any client records. Do not claim a current Power BI `.pbix` or trained AI model: the public dashboard is a live Streamlit app; SQL schema and queries are migration starting points.

## Release checklist

- Confirm fictional data only in `public_data/`, workbook and deck.
- Keep `private_working/`, `.env`, `.streamlit/secrets.toml`, database files and any contact lists out of Git.
- Run `python -m unittest discover -s tests -v` and `python scripts/check_release.py`.
- Inspect screenshots of the deployed app, then add the URL to README. No live URL is claimed before deployment.
