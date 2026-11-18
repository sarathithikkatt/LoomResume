-- GIN index on jd_sessions.keywords for efficient keyword queries
CREATE INDEX IF NOT EXISTS idx_jd_sessions_keywords ON jd_sessions USING GIN (keywords);
