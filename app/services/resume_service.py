"""
Resume Generation and PDF Export Service.

Assembles tailored resumes from experience nodes, role refractions, projects,
and skills matching a target Job Description, and renders ATS-optimized HTML and PDF.
"""

import uuid
from typing import Any
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.models import ExperienceNode, JDSession, Project, Refraction, ResumeOutput, SkillsProfile, User
from app.services.jd_service import jd_service
from app.services.refraction_service import refraction_service

logger = get_logger(__name__)


# ── Clean ATS-Optimized CSS Stylesheets & Templates ──────────────────

RESUME_CSS_MODERN = """
  @page {
    size: letter;
    margin: 0.55in 0.6in;
  }
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  body {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    color: #1a1a1a;
    line-height: 1.4;
    font-size: 10pt;
    background: #ffffff;
  }
  header {
    text-align: center;
    border-bottom: 2px solid #2b2b2b;
    padding-bottom: 8px;
    margin-bottom: 12px;
  }
  h1 {
    font-size: 20pt;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: #111827;
    text-transform: uppercase;
  }
  .headline {
    font-size: 11pt;
    font-weight: 600;
    color: #374151;
    margin-top: 2px;
  }
  .contact-bar {
    margin-top: 5px;
    font-size: 9pt;
    color: #4b5563;
  }
  .contact-bar span {
    margin: 0 6px;
  }
  .contact-bar a {
    color: #1d4ed8;
    text-decoration: none;
  }
  section {
    margin-bottom: 12px;
  }
  h2 {
    font-size: 11pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #1f2937;
    border-bottom: 1px solid #d1d5db;
    padding-bottom: 2px;
    margin-bottom: 6px;
  }
  .summary-text {
    font-size: 9.5pt;
    text-align: justify;
    color: #374151;
  }
  .job-block, .project-block {
    margin-bottom: 8px;
  }
  .job-header, .project-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 2px;
  }
  .job-title-company {
    font-size: 10pt;
  }
  .company-name {
    font-weight: 700;
    color: #111827;
  }
  .role-title {
    font-style: italic;
    color: #374151;
  }
  .job-date {
    font-size: 9pt;
    color: #6b7280;
    font-weight: 500;
    text-align: right;
  }
  ul.bullets {
    margin-left: 16px;
    margin-top: 3px;
  }
  ul.bullets li {
    font-size: 9.5pt;
    margin-bottom: 3px;
    color: #1f2937;
    text-align: justify;
  }
  .skills-grid {
    font-size: 9.5pt;
  }
  .skill-row {
    margin-bottom: 3px;
  }
  .skill-category {
    font-weight: 700;
    color: #1f2937;
    display: inline-block;
    min-width: 140px;
  }
  .skill-items {
    color: #374151;
  }
"""

RESUME_CSS_CLASSIC = """
  @page {
    size: letter;
    margin: 0.5in 0.55in;
  }
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  body {
    font-family: 'Georgia', 'Times New Roman', Times, serif;
    color: #111111;
    line-height: 1.35;
    font-size: 10pt;
    background: #ffffff;
  }
  header {
    text-align: center;
    border-bottom: 1.5px solid #111111;
    padding-bottom: 6px;
    margin-bottom: 10px;
  }
  h1 {
    font-size: 19pt;
    font-weight: 700;
    letter-spacing: 1.2px;
    color: #000000;
    text-transform: uppercase;
  }
  .headline {
    font-size: 10.5pt;
    font-style: italic;
    color: #333333;
    margin-top: 2px;
  }
  .contact-bar {
    margin-top: 4px;
    font-size: 8.5pt;
    color: #444444;
  }
  .contact-bar span {
    margin: 0 5px;
  }
  .contact-bar a {
    color: #111111;
    text-decoration: underline;
  }
  section {
    margin-bottom: 10px;
  }
  h2 {
    font-size: 10.5pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #000000;
    border-bottom: 1px solid #222222;
    padding-bottom: 1px;
    margin-bottom: 5px;
  }
  .summary-text {
    font-size: 9.5pt;
    text-align: justify;
    color: #222222;
  }
  .job-block, .project-block {
    margin-bottom: 7px;
  }
  .job-header, .project-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 2px;
  }
  .job-title-company {
    font-size: 10pt;
  }
  .company-name {
    font-weight: 700;
    color: #000000;
  }
  .role-title {
    font-style: italic;
    color: #333333;
  }
  .job-date {
    font-size: 9pt;
    color: #333333;
    font-style: italic;
    text-align: right;
  }
  ul.bullets {
    margin-left: 18px;
    margin-top: 2px;
  }
  ul.bullets li {
    font-size: 9.5pt;
    margin-bottom: 2.5px;
    color: #111111;
    text-align: justify;
  }
  .skills-grid {
    font-size: 9.5pt;
  }
  .skill-row {
    margin-bottom: 2px;
  }
  .skill-category {
    font-weight: 700;
    color: #000000;
    display: inline-block;
    min-width: 140px;
  }
  .skill-items {
    color: #222222;
  }
"""

RESUME_CSS_MINIMAL = """
  @page {
    size: letter;
    margin: 0.45in 0.5in;
  }
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #0f172a;
    line-height: 1.35;
    font-size: 9.5pt;
    background: #ffffff;
  }
  header {
    margin-bottom: 10px;
    border-bottom: 2px solid #0f172a;
    padding-bottom: 6px;
  }
  h1 {
    font-size: 18pt;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #0f172a;
  }
  .headline {
    font-size: 10pt;
    font-weight: 600;
    color: #475569;
    margin-top: 1px;
  }
  .contact-bar {
    margin-top: 4px;
    font-size: 8.5pt;
    color: #64748b;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  }
  .contact-bar span {
    margin: 0 5px;
  }
  .contact-bar a {
    color: #0284c7;
    text-decoration: none;
  }
  section {
    margin-bottom: 9px;
  }
  h2 {
    font-size: 9.5pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #0f172a;
    border-bottom: 1px solid #cbd5e1;
    padding-bottom: 1px;
    margin-bottom: 4px;
  }
  .summary-text {
    font-size: 9pt;
    color: #334155;
    text-align: justify;
  }
  .job-block, .project-block {
    margin-bottom: 6px;
  }
  .job-header, .project-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 1px;
  }
  .job-title-company {
    font-size: 9.5pt;
  }
  .company-name {
    font-weight: 700;
    color: #0f172a;
  }
  .role-title {
    color: #475569;
    font-weight: 500;
  }
  .job-date {
    font-size: 8.5pt;
    color: #64748b;
    font-family: 'SFMono-Regular', Consolas, monospace;
    text-align: right;
  }
  ul.bullets {
    margin-left: 14px;
    margin-top: 2px;
  }
  ul.bullets li {
    font-size: 9pt;
    margin-bottom: 2px;
    color: #1e293b;
    text-align: justify;
  }
  .skills-grid {
    font-size: 9pt;
  }
  .skill-row {
    margin-bottom: 2px;
  }
  .skill-category {
    font-weight: 700;
    color: #0f172a;
    display: inline-block;
    min-width: 130px;
    font-family: 'SFMono-Regular', Consolas, monospace;
    font-size: 8.5pt;
  }
  .skill-items {
    color: #334155;
  }
"""

RESUME_CSS_EXECUTIVE = """
  @page {
    size: letter;
    margin: 0.5in 0.55in;
  }
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    color: #1e293b;
    line-height: 1.4;
    font-size: 9.8pt;
    background: #ffffff;
  }
  header {
    border-bottom: 3px solid #1e3a8a;
    padding-bottom: 8px;
    margin-bottom: 12px;
  }
  h1 {
    font-size: 21pt;
    font-weight: 800;
    letter-spacing: -0.3px;
    color: #1e3a8a;
  }
  .headline {
    font-size: 11pt;
    font-weight: 600;
    color: #475569;
    margin-top: 2px;
  }
  .contact-bar {
    margin-top: 5px;
    font-size: 9pt;
    color: #64748b;
  }
  .contact-bar span {
    margin: 0 6px;
  }
  .contact-bar a {
    color: #1e3a8a;
    text-decoration: none;
    font-weight: 500;
  }
  section {
    margin-bottom: 11px;
  }
  h2 {
    font-size: 10.5pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #1e3a8a;
    border-left: 3px solid #1e3a8a;
    padding-left: 6px;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 2px;
    margin-bottom: 6px;
  }
  .summary-text {
    font-size: 9.5pt;
    color: #334155;
    text-align: justify;
  }
  .job-block, .project-block {
    margin-bottom: 8px;
  }
  .job-header, .project-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 2px;
  }
  .job-title-company {
    font-size: 10pt;
  }
  .company-name {
    font-weight: 700;
    color: #0f172a;
  }
  .role-title {
    color: #2563eb;
    font-weight: 600;
  }
  .job-date {
    font-size: 8.8pt;
    color: #64748b;
    font-weight: 500;
    text-align: right;
  }
  ul.bullets {
    margin-left: 16px;
    margin-top: 3px;
  }
  ul.bullets li {
    font-size: 9.4pt;
    margin-bottom: 2.5px;
    color: #1e293b;
    text-align: justify;
  }
  .skills-grid {
    font-size: 9.4pt;
  }
  .skill-row {
    margin-bottom: 3px;
  }
  .skill-category {
    font-weight: 700;
    color: #1e3a8a;
    display: inline-block;
    min-width: 140px;
  }
  .skill-items {
    color: #334155;
  }
"""

RESUME_CSS_TEMPLATES: dict[str, str] = {
    "modern": RESUME_CSS_MODERN,
    "classic": RESUME_CSS_CLASSIC,
    "minimal": RESUME_CSS_MINIMAL,
    "executive": RESUME_CSS_EXECUTIVE,
}

def _build_html_document(css: str, body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
{css}
</style>
</head>
<body>
{body_html}
</body>
</html>"""

# Alias for backward compatibility
RESUME_HTML_TEMPLATE = _build_html_document(RESUME_CSS_MODERN, "{body}")


class ResumeService:
    """Orchestrates tailored resume generation and PDF rendering."""

    async def generate_resume_for_jd(
        self,
        jd_session_id: str,
        user_id: str,
        db: Session,
        lens: str | None = None,
        template: str = "modern",
        top_experience_nodes: int = 6,
        top_projects: int = 3,
    ) -> dict[str, Any]:
        """
        Assemble and persist a tailored resume for a specific Job Description.

        1. Fetches user data.
        2. Detects or uses specified lens.
        3. Retrieves top matching experience nodes & projects for the JD.
        4. Replaces original raw_text with refracted bullet points when available.
        5. Formats structured HTML according to the selected styling template and saves to `resume_outputs`.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User not found: {user_id}")

        jd_session = db.query(JDSession).filter(JDSession.id == jd_session_id).first()
        if not jd_session:
            raise ValueError(f"JD Session not found: {jd_session_id}")

        # Choose lens
        selected_lens = lens or refraction_service._auto_select_lens(jd_session.keywords or [])
        logger.info(f"Generating resume for user={user_id}, session={jd_session_id}, lens={selected_lens}, template={template}")

        # Find top matching nodes
        relevant_nodes = jd_service.find_relevant_nodes(
            jd_session_id=jd_session_id,
            user_id=user_id,
            db=db,
            top_k=top_experience_nodes,
        )

        node_ids = [n["node_id"] for n in relevant_nodes]

        # Fetch refractions for these nodes under the selected lens
        refractions_map = {}
        if node_ids:
            refs = db.query(Refraction).filter(
                Refraction.user_id == user_id,
                Refraction.lens == selected_lens,
                Refraction.source_id.in_(node_ids),
            ).all()
            refractions_map = {str(r.source_id): r.reframed_text for r in refs}

        # Build experience structures grouped by company
        grouped_exp: dict[str, dict[str, Any]] = {}
        used_node_uuids = []

        # Get full node records for company/role details
        for node_info in relevant_nodes:
            n_id = node_info["node_id"]
            node_record = db.query(ExperienceNode).filter(ExperienceNode.id == n_id).first()
            if not node_record:
                continue

            used_node_uuids.append(node_record.id)
            bullet_text = refractions_map.get(n_id, node_record.raw_text)

            key = f"{node_record.company}::{node_record.role}"
            if key not in grouped_exp:
                grouped_exp[key] = {
                    "company": node_record.company,
                    "role": node_record.role,
                    "duration": node_record.duration or "",
                    "bullets": [],
                }
            grouped_exp[key]["bullets"].append(bullet_text)

        # Retrieve relevant projects
        projects_query = db.query(Project).filter(Project.user_id == user_id).limit(top_projects).all()
        used_project_uuids = [p.id for p in projects_query]

        # Retrieve skills
        skills_records = db.query(SkillsProfile).filter(SkillsProfile.user_id == user_id).all()

        # Build HTML content
        html_content = self.render_html(
            user=user,
            grouped_experience=list(grouped_exp.values()),
            projects=projects_query,
            skills=skills_records,
            selected_lens=selected_lens,
            template=template,
        )

        # Save to resume_outputs
        resume_record = ResumeOutput(
            user_id=user.id,
            experience_node_ids=used_node_uuids,
            project_ids=used_project_uuids,
            final_content=html_content,
        )
        db.add(resume_record)
        db.commit()

        logger.info(f"Resume generated successfully: id={resume_record.id}")

        return {
            "resume_id": str(resume_record.id),
            "user_id": str(user.id),
            "jd_session_id": jd_session_id,
            "lens": selected_lens,
            "template": template,
            "nodes_count": len(used_node_uuids),
            "projects_count": len(used_project_uuids),
            "final_content": html_content,
            "created_at": resume_record.created_at.isoformat() if resume_record.created_at else None,
        }

    def render_html(
        self,
        user: User,
        grouped_experience: list[dict[str, Any]],
        projects: list[Project],
        skills: list[SkillsProfile],
        selected_lens: str | None = None,
        template: str = "modern",
    ) -> str:
        """Render the complete resume HTML document using the specified template."""
        personal_info = user.personal_info or {}
        name = personal_info.get("name", "Software Engineer")
        label = personal_info.get("label", "")
        email = user.email
        phone = personal_info.get("phone", "")
        location = personal_info.get("location", "")
        linkedin = personal_info.get("linkedin", "")
        github = personal_info.get("github", "")

        label_html = f'<div class="headline">{label}</div>' if label else ""

        # Contact items
        items = []
        if email:
            items.append(f'<a href="mailto:{email}">{email}</a>')
        if phone:
            items.append(phone)
        if location:
            items.append(location)
        if linkedin:
            items.append(f'<a href="{linkedin}">LinkedIn</a>')
        if github:
            items.append(f'<a href="{github}">GitHub</a>')
        contact_items = " &bull; ".join(items)

        # Summary section
        summary_section = ""
        summary_text = user.summary or personal_info.get("summary", "")
        if summary_text:
            summary_section = f"""
            <section id="summary">
              <h2>Professional Summary</h2>
              <p class="summary-text">{summary_text}</p>
            </section>
            """

        # Experience section
        exp_blocks = []
        for exp in grouped_experience:
            bullets_li = "".join(f"<li>{b}</li>" for b in exp.get("bullets", []))
            block = f"""
            <div class="job-block">
              <div class="job-header">
                <div class="job-title-company">
                  <span class="company-name">{exp['company']}</span> &mdash;
                  <span class="role-title">{exp['role']}</span>
                </div>
                <div class="job-date">{exp.get('duration', '')}</div>
              </div>
              <ul class="bullets">
                {bullets_li}
              </ul>
            </div>
            """
            exp_blocks.append(block)
        experience_html = "\n".join(exp_blocks) if exp_blocks else "<p>No experience entries provided.</p>"

        # Projects section
        projects_section = ""
        if projects:
            proj_blocks = []
            for p in projects:
                tags_str = f" | <em>{', '.join(p.tags)}</em>" if p.tags else ""
                proj_blocks.append(f"""
                <div class="project-block">
                  <div class="project-header">
                    <span class="company-name">{p.name}</span>{tags_str}
                  </div>
                  <ul class="bullets">
                    <li>{p.description or ''}</li>
                  </ul>
                </div>
                """)
            projects_section = f"""
            <section id="projects">
              <h2>Key Projects</h2>
              {"".join(proj_blocks)}
            </section>
            """

        # Skills section
        skills_section = ""
        if skills:
            categories: dict[str, list[str]] = {}
            for s in skills:
                cat = s.category or "Technical Skills"
                categories.setdefault(cat, []).append(s.skill_name)

            skill_rows = []
            for cat, names in categories.items():
                skill_rows.append(f"""
                <div class="skill-row">
                  <span class="skill-category">{cat}:</span>
                  <span class="skill-items">{', '.join(names)}</span>
                </div>
                """)
            skills_section = f"""
            <section id="skills">
              <h2>Technical Skills</h2>
              <div class="skills-grid">
                {"".join(skill_rows)}
              </div>
            </section>
            """

        exp_title = (
            "Executive Experience"
            if template.lower() == "executive"
            else "Experience"
            if template.lower() in ("classic", "minimal")
            else "Professional Experience"
        )

        body_html = f"""
<header>
  <h1>{name}</h1>
  {label_html}
  <div class="contact-bar">
    {contact_items}
  </div>
</header>

{summary_section}

<section id="experience">
  <h2>{exp_title}</h2>
  {experience_html}
</section>

{projects_section}

{skills_section}
"""
        css = RESUME_CSS_TEMPLATES.get(template.lower(), RESUME_CSS_TEMPLATES["modern"])
        return _build_html_document(css, body_html)

    def re_render_resume_template(
        self,
        resume_id: str,
        template: str,
        db: Session,
    ) -> str:
        """Re-render an existing resume with a newly selected style template."""
        resume = db.query(ResumeOutput).filter(ResumeOutput.id == resume_id).first()
        if not resume:
            raise ValueError(f"Resume not found: {resume_id}")

        user = db.query(User).filter(User.id == resume.user_id).first()
        if not user:
            raise ValueError(f"User not found: {resume.user_id}")

        # Fetch nodes
        nodes = []
        if resume.experience_node_ids:
            nodes = db.query(ExperienceNode).filter(ExperienceNode.id.in_(resume.experience_node_ids)).all()

        # Group experience
        grouped_exp: dict[str, dict[str, Any]] = {}
        for node in nodes:
            key = f"{node.company}::{node.role}"
            if key not in grouped_exp:
                grouped_exp[key] = {
                    "company": node.company,
                    "role": node.role,
                    "duration": node.duration or "",
                    "bullets": [],
                }
            grouped_exp[key]["bullets"].append(node.raw_text)

        # Projects
        projects = []
        if resume.project_ids:
            projects = db.query(Project).filter(Project.id.in_(resume.project_ids)).all()

        # Skills
        skills = db.query(SkillsProfile).filter(SkillsProfile.user_id == user.id).all()

        new_html = self.render_html(
            user=user,
            grouped_experience=list(grouped_exp.values()),
            projects=projects,
            skills=skills,
            template=template,
        )

        resume.final_content = new_html
        db.commit()
        return new_html

    def render_pdf(self, html_content: str) -> bytes:
        """Render HTML string to PDF bytes using WeasyPrint with pure-Python fallback."""
        try:
            from weasyprint import HTML
            return HTML(string=html_content).write_pdf()
        except (ImportError, OSError, RuntimeError) as e:
            logger.warning(f"WeasyPrint unavailable ({e}), using pure-Python PDF fallback.")
            return self._render_pdf_fallback(html_content)

    def _render_pdf_fallback(self, html_content: str) -> bytes:
        """Pure-Python PDF generator fallback using pydyf when GTK3/Pango is unavailable."""
        import io
        import re
        import pydyf

        # Extract basic text lines from HTML
        text_content = re.sub(r"<[^>]+>", " ", html_content)
        lines = [line.strip() for line in text_content.splitlines() if line.strip()]

        doc = pydyf.PDF()
        stream_commands = [b"BT /F1 10 Tf 50 750 Td"]
        for line in lines[:50]:
            safe_line = re.sub(r"[\\()]", "", line)[:90]
            stream_commands.append(f"({safe_line}) Tj 0 -14 Td".encode("latin-1", errors="replace"))

        stream_commands.append(b"ET")
        stream = pydyf.Stream(stream_commands)
        doc.add_page(stream)

        out = io.BytesIO()
        doc.write(out)
        return out.getvalue()


# Module-level singleton
resume_service = ResumeService()
