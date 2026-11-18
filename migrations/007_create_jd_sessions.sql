CREATE TABLE jd_sessions (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id        UUID REFERENCES users(id) ON DELETE CASCADE,
    jd_text        TEXT NOT NULL,
    keywords       TEXT[],
    jd_embedding   VECTOR(768),
    created_at     TIMESTAMPTZ DEFAULT now()
);
