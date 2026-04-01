from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


REQUIRED_MANUAL_FIELDS = (
    "USER_NAME",
    "USER_PHONE",
    "TARGET_POSITIONS",
    "WORK_HOURS",
    "MIN_SALARY",
)


@dataclass(frozen=True)
class AppConfig:
    base_dir: Path
    cv_link: str
    user_name: str
    user_phone: str
    user_email: str
    user_linkedin: str
    user_portfolio: str
    target_positions: str
    target_industries: str
    target_locations: str
    work_hours: str
    min_salary: str

    @property
    def first_position(self) -> str:
        raw = self.target_positions.strip()
        return raw.split(",")[0].strip() if raw else "Software Engineer"


def load_env_file(env_path: Path) -> bool:
    """
    Load KEY=VALUE lines from .env into process environment.
    Existing env vars are preserved.
    """
    if not env_path.exists():
        return False

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
    return True


def _get_env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def build_config(base_dir: Path) -> AppConfig:
    env_path = base_dir / ".env"
    load_env_file(env_path)

    return AppConfig(
        base_dir=base_dir,
        cv_link=_get_env("CV_LINK"),
        user_name=_get_env("USER_NAME"),
        user_phone=_get_env("USER_PHONE"),
        user_email=_get_env("USER_EMAIL"),
        user_linkedin=_get_env("USER_LINKEDIN"),
        user_portfolio=_get_env("USER_PORTFOLIO"),
        target_positions=_get_env("TARGET_POSITIONS"),
        target_industries=_get_env("TARGET_INDUSTRIES"),
        target_locations=_get_env("TARGET_LOCATIONS"),
        work_hours=_get_env("WORK_HOURS"),
        min_salary=_get_env("MIN_SALARY"),
    )


def validate_config(config: AppConfig) -> tuple[bool, list[str]]:
    missing: list[str] = []

    has_cv = bool(config.cv_link and Path(config.cv_link).exists())
    has_manual = all(_get_env(field) for field in REQUIRED_MANUAL_FIELDS)
    if not (has_cv or has_manual):
        missing.extend(
            field for field in REQUIRED_MANUAL_FIELDS if not _get_env(field)
        )

    return (len(missing) == 0 or has_cv, missing)
