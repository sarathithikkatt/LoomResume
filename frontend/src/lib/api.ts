/**
 * API client for the LoomResume FastAPI backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface VaultData {
  user: {
    id: string;
    email: string;
    personal_info: {
      name?: string;
      label?: string;
      phone?: string;
      location?: string;
      linkedin?: string;
      github?: string;
    };
    summary?: string;
  } | null;
  nodes: Array<{
    id: string;
    company: string;
    role: string;
    duration?: string;
    raw_text: string;
    tags: string[];
  }>;
  projects: Array<{
    id: string;
    name: string;
    description: string;
    tags: string[];
  }>;
  skills: Array<{
    id: string;
    skill_name: string;
    category?: string;
  }>;
}

export interface JDAnalysis {
  session_id: string;
  keywords: string[];
  role_level: string;
  technologies: string[];
}

export interface JDScore {
  overall_score: number;
  semantic_score: number;
  keyword_score: number;
  present_keywords: string[];
  missing_keywords: string[];
  top_matches: Array<{
    node_id: string;
    company: string;
    role: string;
    raw_text: string;
    similarity: number;
  }>;
}

export interface RefractionResult {
  refraction_id: string;
  source_id: string;
  lens: string;
  original_text: string;
  reframed_text: string;
  verification: {
    passed: boolean;
    facts: {
      passed: boolean;
      preservation_rate: number;
      missing_metrics: string[];
      missing_techs: string[];
    };
    truncation: {
      is_truncated: boolean;
      length_ratio: number;
    };
    diff: {
      similarity_ratio: number;
      additions_count: number;
      deletions_count: number;
    };
  };
  attempts: number;
}

export interface ResumeData {
  resume_id: string;
  user_id: string;
  jd_session_id?: string;
  lens?: string;
  nodes_count: number;
  projects_count: number;
  final_content: string;
  created_at?: string;
}

export interface GapProject {
  jd_session_id: string;
  user_id: string;
  targeted_gaps: string[];
  project_blueprint: {
    project_name: string;
    tagline: string;
    architecture_summary: string;
    technologies: string[];
    milestones: Array<{
      phase: string;
      deliverables: string[];
    }>;
    metrics_to_measure: string[];
    resume_bullet_points: string[];
  };
}

export interface MockInterview {
  jd_session_id: string;
  target_skills: string[];
  interview_questions: Array<{
    topic: string;
    question: string;
    what_to_look_for: string;
  }>;
}

export const api = {
  async getHealth() {
    const res = await fetch(`${API_BASE}/health/`);
    return res.json();
  },

  async getVault(): Promise<VaultData> {
    const res = await fetch(`${API_BASE}/ingest/vault`);
    if (!res.ok) throw new Error("Failed to fetch vault data");
    return res.json();
  },

  async triggerIngest(): Promise<Record<string, unknown>> {
    const res = await fetch(`${API_BASE}/ingest/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    if (!res.ok) throw new Error("Ingestion failed");
    return res.json();
  },

  async analyzeJD(jdText: string, userEmail: string): Promise<JDAnalysis> {
    const res = await fetch(`${API_BASE}/jd/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jd_text: jdText, user_email: userEmail }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "JD Analysis failed" }));
      throw new Error(err.detail || "JD Analysis failed");
    }
    return res.json();
  },

  async getJDScore(sessionId: string, userId: string): Promise<JDScore> {
    const res = await fetch(`${API_BASE}/jd/${sessionId}/score?user_id=${userId}`);
    if (!res.ok) throw new Error("Failed to score JD");
    return res.json();
  },

  async refractNode(nodeId: string, lens: string, userId: string): Promise<RefractionResult> {
    const res = await fetch(`${API_BASE}/refraction/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ experience_node_id: nodeId, lens, user_id: userId }),
    });
    if (!res.ok) throw new Error("Refraction failed");
    return res.json();
  },

  async generateResume(
    sessionId: string,
    userId: string,
    lens?: string,
    template: string = "modern"
  ): Promise<ResumeData> {
    const res = await fetch(`${API_BASE}/resume/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jd_session_id: sessionId, user_id: userId, lens, template }),
    });
    if (!res.ok) throw new Error("Resume generation failed");
    return res.json();
  },

  async switchResumeTemplate(resumeId: string, template: string): Promise<{ resume_id: string; final_content: string }> {
    const res = await fetch(`${API_BASE}/resume/${resumeId}/template`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ template }),
    });
    if (!res.ok) throw new Error("Failed to switch resume template");
    return res.json();
  },

  async createNode(data: {
    company: string;
    role: string;
    duration?: string;
    raw_text: string;
    tags?: string[];
  }): Promise<any> {
    const res = await fetch(`${API_BASE}/ingest/nodes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to create experience node");
    return res.json();
  },

  async updateNode(
    nodeId: string,
    data: {
      company?: string;
      role?: string;
      duration?: string;
      raw_text?: string;
      tags?: string[];
    }
  ): Promise<any> {
    const res = await fetch(`${API_BASE}/ingest/nodes/${nodeId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to update experience node");
    return res.json();
  },

  async deleteNode(nodeId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/ingest/nodes/${nodeId}`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete experience node");
    return res.json();
  },

  async createSkill(data: { skill_name: string; category?: string }): Promise<any> {
    const res = await fetch(`${API_BASE}/ingest/skills`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to add skill");
    return res.json();
  },

  async deleteSkill(skillId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/ingest/skills/${skillId}`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete skill");
    return res.json();
  },

  async createProject(data: { name: string; description: string; tags?: string[] }): Promise<any> {
    const res = await fetch(`${API_BASE}/ingest/projects`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to create project");
    return res.json();
  },

  async updateProject(
    projectId: string,
    data: { name?: string; description?: string; tags?: string[] }
  ): Promise<any> {
    const res = await fetch(`${API_BASE}/ingest/projects/${projectId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to update project");
    return res.json();
  },

  async deleteProject(projectId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/ingest/projects/${projectId}`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete project");
    return res.json();
  },

  async updateProfile(data: {
    name?: string;
    label?: string;
    phone?: string;
    location?: string;
    linkedin?: string;
    github?: string;
    summary?: string;
  }): Promise<any> {
    const res = await fetch(`${API_BASE}/ingest/profile`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to update profile");
    return res.json();
  },

  getResumePdfUrl(resumeId: string): string {
    return `${API_BASE}/resume/${resumeId}/pdf`;
  },

  async architectGapProject(sessionId: string, userId: string): Promise<GapProject> {
    const res = await fetch(`${API_BASE}/agents/gap-project`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jd_session_id: sessionId, user_id: userId }),
    });
    if (!res.ok) throw new Error("Gap project architecting failed");
    return res.json();
  },

  async generateMockInterview(sessionId: string, userId: string): Promise<MockInterview> {
    const res = await fetch(`${API_BASE}/agents/mock-interview`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jd_session_id: sessionId, user_id: userId }),
    });
    if (!res.ok) throw new Error("Mock interview generation failed");
    return res.json();
  },

  async chat(message: string): Promise<{ response: string }> {
    const res = await fetch(`${API_BASE}/chat/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: "default-session", message }),
    });
    if (!res.ok) throw new Error("Chat failed");
    return res.json();
  },
};
