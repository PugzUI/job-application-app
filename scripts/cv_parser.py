import argparse
import subprocess
import json
import re
from pathlib import Path


def extract_text_from_pdf(pdf_path: Path) -> str:
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    result = subprocess.run(
        ["pdftotext", str(pdf_path), "-"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"pdftotext failed with code {result.returncode}: {result.stderr.strip()}"
        )
    return result.stdout


def parse_personal_info(text: str) -> dict:
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    phone_pattern = r"\+?\d[\d\s\-()]{8,}\d"
    linkedin_pattern = r"(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9-]+/?"

    email = re.search(email_pattern, text)
    phone = re.search(phone_pattern, text)
    linkedin = re.search(linkedin_pattern, text)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    name = lines[0] if lines else ""

    return {
        "full_name": name or None,
        "email": email.group(0) if email else None,
        "phone": phone.group(0) if phone else None,
        "linkedin": linkedin.group(0) if linkedin else None
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract basic personal info from a CV PDF.")
    parser.add_argument("pdf_path", help="Path to CV PDF.")
    parser.add_argument(
        "--output",
        help="Optional output JSON path. If omitted, prints to stdout.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        parsed = parse_personal_info(extract_text_from_pdf(Path(args.pdf_path)))
    except Exception as exc:
        print(f"[!] CV parsing failed: {exc}")
        return 1

    payload = json.dumps(parsed, indent=2)
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(payload + "\n", encoding="utf-8")
        print(f"[+] Wrote extracted info to {output_path}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
