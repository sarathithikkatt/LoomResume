CREATE TABLE users (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email        TEXT NOT NULL UNIQUE,
    personal_info JSONB,
    summary      TEXT,
    created_at   TIMESTAMPTZ DEFAULT now()
);
