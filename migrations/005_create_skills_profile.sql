CREATE TABLE skills_profile (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    skill_name  TEXT NOT NULL,
    category    TEXT,
    details     JSONB,
    created_at  TIMESTAMPTZ DEFAULT now()
);
