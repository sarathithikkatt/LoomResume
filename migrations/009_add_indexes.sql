CREATE INDEX ON experience_nodes USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON projects         USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON refractions      USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON jd_sessions      USING hnsw (jd_embedding vector_cosine_ops);

CREATE INDEX ON experience_nodes USING GIN (tags);
CREATE INDEX ON projects         USING GIN (tags);

CREATE INDEX ON experience_nodes (user_id);
CREATE INDEX ON experience_nodes (user_id, company);
CREATE INDEX ON refractions      (source_id, lens);
