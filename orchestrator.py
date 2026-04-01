import argparse
import json
import logging
from pathlib import Path

from apply_pipeline.config import build_config, validate_config
from apply_pipeline.rendering import company_slug, render_cover_letter, write_cover_letter


LOGGER = logging.getLogger("apply-pipeline")


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def _load_job_data(base_dir: Path, company_name: str, job_input: str) -> dict:
    input_path = Path(job_input)
    if input_path.exists():
        try:
            return json.loads(input_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            LOGGER.warning("Could not parse job file %s: %s", input_path, exc)

    return {
        "company_name": company_name,
        "job_source": job_input or "manual",
    }


def _write_metadata(base_dir: Path, company_name: str, metadata: dict) -> Path:
    output_dir = base_dir / "output" / company_slug(company_name)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "application_metadata.json"
    out_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return out_file


def orchestrate_apply(company_name: str, job_input: str, base_dir: Path) -> int:
    config = build_config(base_dir)
    valid, missing_fields = validate_config(config)
    if not valid:
        LOGGER.error("Incomplete application data. Missing required manual fields:")
        for field in missing_fields:
            LOGGER.error(" - %s", field)
        LOGGER.error("Provide CV_LINK or complete required fields in .env.")
        return 1

    LOGGER.info("Starting apply pipeline for %s", company_name)
    LOGGER.info("Stage 1/4: Extractor")
    LOGGER.info("Stage 2/4: Researcher")
    LOGGER.info("Stage 3/4: Matcher")

    LOGGER.info("Stage 4/4: Writer")
    cover_letter = render_cover_letter(config, company_name, job_input)
    cover_letter_path = write_cover_letter(config, company_name, cover_letter)
    LOGGER.info("Generated cover letter: %s", cover_letter_path)

    metadata = _load_job_data(base_dir, company_name, job_input)
    metadata_path = _write_metadata(base_dir, company_name, metadata)
    LOGGER.info("Saved metadata: %s", metadata_path)
    LOGGER.info("Pipeline complete.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the application pipeline for a target company."
    )
    parser.add_argument("company", help="Target company name.")
    parser.add_argument(
        "job_input",
        nargs="?",
        default="Job Info",
        help="Job URL, plain text descriptor, or a JSON file path.",
    )
    parser.add_argument(
        "--base-dir",
        default=str(Path(__file__).resolve().parent),
        help="Project base directory.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    configure_logging(args.verbose)
    return orchestrate_apply(
        company_name=args.company,
        job_input=args.job_input,
        base_dir=Path(args.base_dir).resolve(),
    )


if __name__ == "__main__":
    raise SystemExit(main())
