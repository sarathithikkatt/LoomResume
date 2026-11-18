from pydantic import BaseModel


class ChatRequest(BaseModel):
    chat_id: str = "default"
    message: str
    model: str | None = None  # LiteLLM model string; defaults to settings.LLM_DEFAULT_MODEL
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
    template: str = "modern"
    top_experience_nodes: int = 6
    top_projects: int = 3


class ResumeGenerateResponse(BaseModel):
    resume_id: str
    user_id: str
    jd_session_id: str | None = None
    lens: str | None = None
    template: str = "modern"
    nodes_count: int
    projects_count: int
    final_content: str
    created_at: str | None = None


class ResumeSwitchTemplateRequest(BaseModel):
    template: str = "modern"


class ResumeDetailResponse(BaseModel):
    resume_id: str
    user_id: str
    final_content: str
    created_at: str | None = None


class ResumeRenderPDFRequest(BaseModel):
    html_content: str


# ── Vault CRUD Schemas ──────────────────────────────────────────────

class ExperienceNodeCreate(BaseModel):
    company: str
    role: str
    duration: str | None = None
    raw_text: str
    tags: list[str] = []


class ExperienceNodeUpdate(BaseModel):
    company: str | None = None
    role: str | None = None
    duration: str | None = None
    raw_text: str | None = None
    tags: list[str] | None = None


class SkillCreate(BaseModel):
    skill_name: str
    category: str | None = "Technical Skills"


class ProjectCreate(BaseModel):
    name: str
    description: str
    tags: list[str] = []


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    tags: list[str] | None = None


class UserProfileUpdate(BaseModel):
    name: str | None = None
    label: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin: str | None = None
    github: str | None = None
    summary: str | None = None



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
