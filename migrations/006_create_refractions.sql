CREATE TABLE refractions (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id      UUID NOT NULL,
    source_type    TEXT NOT NULL,
    user_id        UUID REFERENCES users(id) ON DELETE CASCADE,
    lens           TEXT NOT NULL,
    reframed_text  TEXT NOT NULL,
    embedding      VECTOR(768),
    created_at     TIMESTAMPTZ DEFAULT now(),
    UNIQUE (source_id, lens)
);
