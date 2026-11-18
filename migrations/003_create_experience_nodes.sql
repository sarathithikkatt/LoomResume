CREATE TABLE experience_nodes (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    company     TEXT NOT NULL,
    role        TEXT NOT NULL,
    duration    TEXT,
    start_date  DATE,
    end_date    DATE,
    raw_text    TEXT NOT NULL,
    tags        TEXT[],
    embedding   VECTOR(768),
    created_at  TIMESTAMPTZ DEFAULT now()
);
