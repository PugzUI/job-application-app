import argparse
from pathlib import Path

from orchestrator import configure_logging, orchestrate_apply


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Backwards-compatible entrypoint for running apply pipeline."
    )
    parser.add_argument("company", nargs="?", default="Target Company")
    parser.add_argument("job_input", nargs="?", default="Job Info")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    configure_logging(verbose=False)
    return orchestrate_apply(
        company_name=args.company,
        job_input=args.job_input,
        base_dir=Path(__file__).resolve().parent,
    )


if __name__ == "__main__":
    raise SystemExit(main())
