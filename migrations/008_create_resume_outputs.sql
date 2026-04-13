CREATE TABLE resume_outputs (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id        UUID REFERENCES users(id) ON DELETE CASCADE,
    experience_node_ids UUID[],
    project_ids    UUID[],
    final_content  TEXT NOT NULL,
    created_at     TIMESTAMPTZ DEFAULT now()
);
