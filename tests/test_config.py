import os
from pathlib import Path

from apply_pipeline.config import build_config, validate_config


def test_build_config_reads_env(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                'USER_NAME="Example Applicant"',
                'USER_PHONE="+1 555 123 4567"',
                'TARGET_POSITIONS="Backend Engineer,Platform Engineer"',
                'WORK_HOURS="Full-time"',
                'MIN_SALARY="120000"',
            ]
        ),
        encoding="utf-8",
    )

    cwd_before = Path.cwd()
    os.chdir(tmp_path)
    try:
        cfg = build_config(tmp_path)
        ok, missing = validate_config(cfg)
    finally:
        os.chdir(cwd_before)

    assert cfg.user_name == "Example Applicant"
    assert cfg.first_position == "Backend Engineer"
    assert ok is True
    assert missing == []
