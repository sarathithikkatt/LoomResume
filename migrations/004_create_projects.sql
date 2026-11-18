CREATE TABLE projects (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    description TEXT,
    tags        TEXT[],
    embedding   VECTOR(768),
    created_at  TIMESTAMPTZ DEFAULT now()
);
