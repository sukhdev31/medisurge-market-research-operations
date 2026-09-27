-- PostgreSQL examples after loading approved data to the normalized model.
SELECT h.state, o.service_line, COUNT(*) AS accounts,
       COUNT(*) FILTER (WHERE h.verification_status = 'Verified') AS verified_accounts
FROM hospitals h JOIN opportunities o USING (hospital_id)
GROUP BY h.state, o.service_line ORDER BY accounts DESC;

-- Source coverage of opportunity signals. Unknown must not be interpreted as absent.
SELECT o.service_line,
       COUNT(*) FILTER (WHERE o.score_expansion IS NOT NULL) AS rated,
       COUNT(*) FILTER (WHERE o.score_expansion IS NOT NULL AND o.signal_source_id IS NULL) AS missing_signal_source
FROM opportunities o GROUP BY o.service_line;

-- Operational stage mix without exposing identities.
SELECT pipeline_stage, COUNT(*) AS accounts
FROM opportunities GROUP BY pipeline_stage ORDER BY accounts DESC;
