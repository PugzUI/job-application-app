from pathlib import Path

import pytest

from apply_pipeline.config import AppConfig
from apply_pipeline.rendering import render_cover_letter


def _base_config(tmp_path: Path) -> AppConfig:
    return AppConfig(
        base_dir=tmp_path,
        cv_link="",
        user_name="Example Applicant",
        user_phone="+1 555 123 4567",
        user_email="applicant@example.com",
        user_linkedin="https://example.com/linkedin-profile",
        user_portfolio="https://example.com",
        target_positions="Backend Engineer,Platform Engineer",
        target_industries="Software",
        target_locations="Remote",
        work_hours="Full-time",
        min_salary="120000",
    )


def test_render_cover_letter_replaces_template_fields(tmp_path: Path) -> None:
    (tmp_path / "template.md").write_text(
        "Hello {{YOUR_NAME}} applying to {{COMPANY_NAME}} as {{JOB_TITLE}}.\n"
        "Phone: {{YOUR_PHONE_NUMBER}}\n"
        "Link: {{YOUR_LINKEDIN_OR_PORTFOLIO_LINK}}\n",
        encoding="utf-8",
    )
    cfg = _base_config(tmp_path)
    rendered = render_cover_letter(cfg, "Acme", "LinkedIn")

    assert "Example Applicant" in rendered
    assert "Acme" in rendered
    assert "{{" not in rendered


def test_render_cover_letter_fails_on_unresolved_placeholder(tmp_path: Path) -> None:
    (tmp_path / "template.md").write_text(
        "Hello {{YOUR_NAME}} and {{UNKNOWN_TOKEN}}", encoding="utf-8"
    )
    cfg = _base_config(tmp_path)
    with pytest.raises(ValueError, match="Unresolved placeholders"):
        render_cover_letter(cfg, "Acme", "LinkedIn")
