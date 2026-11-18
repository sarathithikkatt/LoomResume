from pydantic import BaseModel


class ChatRequest(BaseModel):
    chat_id: str
    message: str
    model: str = "gpt-4o"  # LiteLLM model string: "gpt-4o", "claude-sonnet-4-20250514", "ollama/llama3.1"
    system_prompt: str | None = None
    temperature: float = 0.7


class ChatResponse(BaseModel):
    response: str


# ── JD Schemas ──────────────────────────────────────────────────────

class JDAnalyzeRequest(BaseModel):
    jd_text: str
    user_email: str


class JDAnalyzeResponse(BaseModel):
    session_id: str
    keywords: list[str]
    role_level: str
    technologies: list[str]


class JDScoreResponse(BaseModel):
    overall_score: float
    semantic_score: float
    keyword_score: float
    present_keywords: list[str]
    missing_keywords: list[str]
    top_matches: list[dict]


class JDMatchResponse(BaseModel):
    matches: list[dict]


# ── Resume Schemas ──────────────────────────────────────────────────

class ResumeGenerateRequest(BaseModel):
    jd_session_id: str
    user_id: str
    lens: str | None = None
    top_experience_nodes: int = 6
    top_projects: int = 3


class ResumeGenerateResponse(BaseModel):
    resume_id: str
    user_id: str
    jd_session_id: str | None = None
    lens: str | None = None
    nodes_count: int
    projects_count: int
    final_content: str
    created_at: str | None = None


class ResumeDetailResponse(BaseModel):
    resume_id: str
    user_id: str
    final_content: str
    created_at: str | None = None


class ResumeRenderPDFRequest(BaseModel):
    html_content: str



# ── Agent Schemas ───────────────────────────────────────────────────

class GapProjectRequest(BaseModel):
    jd_session_id: str
    user_id: str
    model: str | None = None


class GapProjectResponse(BaseModel):
    jd_session_id: str
    user_id: str
    targeted_gaps: list[str]
    project_blueprint: dict


class MockInterviewRequest(BaseModel):
    jd_session_id: str
    user_id: str
    model: str | None = None


class MockInterviewResponse(BaseModel):
    jd_session_id: str
    target_skills: list[str]
    interview_questions: list[dict]
