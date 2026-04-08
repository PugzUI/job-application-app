# Apply Pipeline

A Python-based application pipeline that generates personalized cover letters from profile data, environment config, and job context.

This started as a quick prototype and has now been hardened into a more refined project with:

- structured CLI workflow
- reusable internal modules
- automated tests for core behavior

## What It Does

- Loads and validates candidate/application data from `.env`
- Builds company-scoped output directories in `output/<company_slug>/`
- Renders `template.md` into a real cover letter with profile data
- Blocks unresolved placeholders (`{{TOKEN}}`, `[Your Name]` patterns)
- Provides a CV parsing utility for extracting personal fields from PDF text
- Writes metadata snapshot for each run

## Project Structure

```text
apply/
├── apply_pipeline/
│   ├── config.py              # env loading + config model + validation
│   └── rendering.py           # template rendering + placeholder checks
├── orchestrator.py            # main CLI pipeline
├── apply_agent.py             # compatibility entrypoint
├── scripts/
│   └── cv_parser.py           # PDF text extraction + personal info parser
├── tests/
│   ├── test_config.py
│   └── test_rendering.py
├── template.md
├── .env.example
├── pyproject.toml
└── output/                    # generated artifacts (gitignored)
```

## Requirements

- Python 3.10+
- `pdftotext` on PATH (for `scripts/cv_parser.py`)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Fill `.env` with either:

- a valid `CV_LINK`, or
- required manual fields:
  - `USER_NAME`
  - `USER_PHONE`
  - `TARGET_POSITIONS`
  - `WORK_HOURS`
  - `MIN_SALARY`

## Usage

### Run the pipeline

```bash
python orchestrator.py "Example Company" "https://example.com/job-posting"
```

Optional flags:

```bash
python orchestrator.py "Example Company" "Job Info" --verbose
python orchestrator.py "Example Company" "job_data.json" --base-dir /path/to/project
```

### Run compatibility entrypoint

```bash
python apply_agent.py "Example Company" "Job Info"
```

### Parse CV into JSON

```bash
python scripts/cv_parser.py "/absolute/path/to/cv.pdf" --output personal_info.json
```

## Outputs

For company `Example Company`, files are generated under:

```text
output/example_company/
```

Typical artifacts:

- `cover_letter.md`
- `application_metadata.json`

## Quality Checks

Run all checks:

```bash
python -m py_compile orchestrator.py apply_agent.py scripts/cv_parser.py
pytest
```

## Roadmap

Next hardening targets:

- richer domain models for job/evidence payloads
- stronger template grammar and style controls
- end-to-end tests for full pipeline runs
- packaging and release automation

## Contributing

Issues and pull requests are welcome, especially around reliability, test coverage, and document quality.

## License

MIT. See `LICENSE`.
