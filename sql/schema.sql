-- Optional PostgreSQL model for a private, approved implementation.
-- The public demo loads CSV in memory and does not store uploads.
CREATE TABLE sources (
    source_id TEXT PRIMARY KEY,
    entity_name TEXT NOT NULL,
    claim TEXT NOT NULL,
    source_url TEXT NOT NULL,
    source_type TEXT NOT NULL,
    checked_date DATE NOT NULL,
    verified_by_human BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT NOT NULL DEFAULT ''
);
CREATE TABLE hospitals (
    hospital_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    segment TEXT NOT NULL,
    bed_band TEXT,
    specialty TEXT,
    verification_status TEXT NOT NULL CHECK (verification_status IN ('Synthetic','Verified','Unverified')),
    checked_date DATE
);
CREATE TABLE opportunities (
    hospital_id TEXT PRIMARY KEY REFERENCES hospitals(hospital_id),
    service_line TEXT NOT NULL CHECK (service_line IN ('CSSD consultancy','NABH readiness','Modular OT')),
    pipeline_stage TEXT NOT NULL,
    score_expansion SMALLINT CHECK (score_expansion BETWEEN 0 AND 5),
    score_surgical SMALLINT CHECK (score_surgical BETWEEN 0 AND 5),
    score_service_fit SMALLINT CHECK (score_service_fit BETWEEN 0 AND 5),
    score_serviceability SMALLINT CHECK (score_serviceability BETWEEN 0 AND 5),
    score_quality SMALLINT CHECK (score_quality BETWEEN 0 AND 5),
    score_strategic SMALLINT CHECK (score_strategic BETWEEN 0 AND 5),
    signal_source_id TEXT REFERENCES sources(source_id),
    quality_source_id TEXT REFERENCES sources(source_id)
);
CREATE TABLE stakeholder_feedback (
    feedback_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reviewed_at TIMESTAMPTZ NOT NULL,
    reviewer_role TEXT NOT NULL,
    version TEXT NOT NULL,
    feedback TEXT NOT NULL,
    action_taken TEXT
);
