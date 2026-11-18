"""
Unit tests for ResumeService — HTML templating and PDF rendering.
"""

from unittest.mock import MagicMock
import pytest
from app.services.resume_service import ResumeService


@pytest.fixture
def resume_svc():
    return ResumeService()


class TestResumeServiceHTML:
    def test_render_html_basic(self, resume_svc):
        mock_user = MagicMock()
        mock_user.email = "sarath@example.com"
        mock_user.summary = "Distributed systems engineer."
        mock_user.personal_info = {
            "name": "Sarath I S",
            "label": "Senior Backend Engineer",
            "phone": "+91 9999999999",
            "location": "Gurgaon, India",
            "linkedin": "https://linkedin.com/in/test",
            "github": "https://github.com/test",
        }

        mock_exp = [
            {
                "company": "Tech Corp",
                "role": "Lead Engineer",
                "duration": "2024 - Present",
                "bullets": [
                    "Engineered distributed queue with 99.99% reliability.",
                    "Reduced p99 latency by 45% using Redis caching.",
                ],
            }
        ]

        mock_project = MagicMock()
        mock_project.name = "Video Processing Engine"
        mock_project.description = "Low-latency video transcoding service."
        mock_project.tags = ["Go", "FFmpeg", "AWS"]

        mock_skill = MagicMock()
        mock_skill.category = "Languages"
        mock_skill.skill_name = "Go"

        html = resume_svc.render_html(
            user=mock_user,
            grouped_experience=mock_exp,
            projects=[mock_project],
            skills=[mock_skill],
            selected_lens="platform",
        )

        assert "SARATH I S" in html.upper()
        assert "Senior Backend Engineer" in html
        assert "sarath@example.com" in html
        assert "Tech Corp" in html
        assert "Lead Engineer" in html
        assert "Engineered distributed queue" in html
        assert "Video Processing Engine" in html
        assert "Technical Skills" in html
        assert "Languages" in html

    def test_render_html_all_templates(self, resume_svc):
        mock_user = MagicMock()
        mock_user.email = "sarath@example.com"
        mock_user.summary = "Distributed systems engineer."
        mock_user.personal_info = {"name": "Sarath I S"}

        mock_exp = [{"company": "Tech Corp", "role": "Lead", "bullets": ["Built scale-out infra."]}]
        mock_skill = MagicMock()
        mock_skill.category = "Tools"
        mock_skill.skill_name = "Docker"

        for template in ["modern", "classic", "minimal", "executive"]:
            html = resume_svc.render_html(
                user=mock_user,
                grouped_experience=mock_exp,
                projects=[],
                skills=[mock_skill],
                template=template,
            )
            assert "Sarath I S" in html
            assert "Tech Corp" in html
            assert "Built scale-out infra." in html


class TestResumeServicePDF:
    def test_render_pdf(self, resume_svc):
        sample_html = "<html><body><h1>Test Resume</h1><p>Sample content</p></body></html>"
        pdf_bytes = resume_svc.render_pdf(sample_html)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF-")
