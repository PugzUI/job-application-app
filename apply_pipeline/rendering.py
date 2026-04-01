from __future__ import annotations

import json
import re
from pathlib import Path

from .config import AppConfig


def read_json_if_exists(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def first_non_empty(*values: str) -> str:
    for value in values:
        if value:
            return str(value).strip()
    return ""


def company_slug(name: str) -> str:
    return name.replace(" ", "_").lower()


def _build_replacements(config: AppConfig, company_name: str, job_input: str) -> dict[str, str]:
    personal = read_json_if_exists(config.base_dir / "personal_info.json")
    insights = read_json_if_exists(config.base_dir / "insights.json")

    user_name = first_non_empty(config.user_name, personal.get("full_name"), "Applicant Name")
    user_phone = first_non_empty(config.user_phone, personal.get("phone"), "Phone not provided")
    user_link = first_non_empty(
        config.user_linkedin,
        config.user_portfolio,
        personal.get("linkedin"),
        personal.get("portfolio"),
        "Link not provided",
    )
    mission = first_non_empty(
        insights.get("mission"),
        f"building practical, high-impact products at {company_name}",
    )
    recent_news = insights.get("recent_news") or []
    interesting_detail = (
        recent_news[0]
        if recent_news
        else f"your recent work in {config.target_industries or 'technology'}"
    )

    return {
        "JOB_TITLE": config.first_position,
        "YOUR_NAME": user_name,
        "HIRING_MANAGER_NAME_OR_TEAM": f"{company_name} Team",
        "COMPANY_NAME": company_name,
        "PLATFORM_NAME": job_input if job_input else "your listing",
        "YOUR_PRIMARY_EXPERTISE": "full-stack engineering and AI automation",
        "HIGH_LEVEL_ACHIEVEMENT": "shipping reliable systems that improve workflow efficiency",
        "COMPANY_MISSION_OR_GOAL": mission,
        "SPECIFIC_COMPANY_VALUE_OR_PROJECT": "translating advanced technology into measurable business outcomes",
        "INTERESTING_DETAIL_FROM_RESEARCH": interesting_detail,
        "RELEVANT_SKILL_OR_DOMAIN": "scalable AI-driven application development",
        "CORE_SKILL_1": "Full-Stack Engineering",
        "ACCOMPLISHMENT_1_OR_HOW_IT_APPLIES_TO_JOB": "building maintainable user-facing and backend systems",
        "CORE_SKILL_2": "AI Workflow Automation",
        "ACCOMPLISHMENT_2_OR_HOW_IT_APPLIES_TO_JOB": "integrating LLM-enabled workflows into practical products",
        "CORE_SKILL_3": "Delivery in Production Contexts",
        "ACCOMPLISHMENT_3_OR_HOW_IT_APPLIES_TO_JOB": "shipping stable features under real-world operational constraints",
        "PRAGMATIC_VALUE_PROPOSITION": "Business-Focused Execution",
        "HOW_YOU_SOLVE_THEIR_SPECIFIC_PAIN_POINT": "aligning technical choices with clear ROI and operational reliability",
        "WORK_ENVIRONMENT_TYPE": "collaborative and delivery-focused",
        "SPECIFIC_OUTCOME_THE_JOB_PROMISES": "high-impact product outcomes",
        "YOUR_PHONE_NUMBER": user_phone,
        "YOUR_LINKEDIN_OR_PORTFOLIO_LINK": user_link,
    }


def render_cover_letter(config: AppConfig, company_name: str, job_input: str) -> str:
    template_path = config.base_dir / "template.md"
    if not template_path.exists():
        raise FileNotFoundError("template.md not found.")

    rendered = template_path.read_text(encoding="utf-8")
    for key, value in _build_replacements(config, company_name, job_input).items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)

    unresolved = re.findall(r"\{\{[^}]+\}\}|\[Your [^\]]+\]", rendered)
    if unresolved:
        unique = ", ".join(sorted(set(unresolved)))
        raise ValueError(f"Unresolved placeholders: {unique}")

    return rendered


def write_cover_letter(config: AppConfig, company_name: str, content: str) -> Path:
    out_dir = config.base_dir / "output" / company_slug(company_name)
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / "cover_letter.md"
    output_path.write_text(content, encoding="utf-8")
    return output_path
