from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path

import markdown
from xhtml2pdf import pisa


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <style>
    @page {{
      size: A4;
      margin: 0.75in;
    }}

    body {{
      font-family: Helvetica, Arial, sans-serif;
      font-size: 11pt;
      line-height: 1.55;
      color: #1f2937;
    }}

    h1, h2, h3, h4, h5, h6 {{
      color: #111827;
      margin-top: 1.2em;
      margin-bottom: 0.45em;
    }}

    p, ul, ol, blockquote, pre {{
      margin: 0 0 0.8em 0;
    }}

    code {{
      font-family: Courier, monospace;
      background: #f3f4f6;
      padding: 2px 4px;
    }}

    pre {{
      background: #f3f4f6;
      border: 1px solid #e5e7eb;
      padding: 10px;
      white-space: pre-wrap;
    }}

    blockquote {{
      border-left: 4px solid #d1d5db;
      padding-left: 12px;
      color: #4b5563;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 1em;
    }}

    th, td {{
      border: 1px solid #d1d5db;
      padding: 6px 8px;
      text-align: left;
    }}

    th {{
      background: #f9fafb;
    }}

    img {{
      max-width: 100%;
      height: auto;
    }}
  </style>
</head>
<body>
{content}
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert a Markdown file to PDF.")
    parser.add_argument("input", type=Path, help="Path to the source Markdown file.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Path to the output PDF file. Defaults to the input filename with a .pdf extension.",
    )
    return parser.parse_args()


def render_markdown(markdown_text: str, title: str) -> str:
    html_body = markdown.markdown(
        markdown_text,
        extensions=["extra", "tables", "fenced_code", "toc"],
        output_format="html5",
    )
    return HTML_TEMPLATE.format(title=title, content=html_body)


def convert_markdown_text_to_pdf_bytes(markdown_text: str, title: str = "document") -> bytes:
    html = render_markdown(markdown_text, title=title)
    buffer = BytesIO()
    result = pisa.CreatePDF(src=html, dest=buffer)

    if result.err:
        raise RuntimeError("PDF generation failed")

    return buffer.getvalue()


def convert_markdown_to_pdf(source: Path, destination: Path) -> None:
    markdown_text = source.read_text(encoding="utf-8")
    pdf_bytes = convert_markdown_text_to_pdf_bytes(markdown_text, title=source.stem)

    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as pdf_file:
        pdf_file.write(pdf_bytes)


def main() -> None:
    args = parse_args()
    source = args.input.resolve()

    if not source.exists():
        raise FileNotFoundError(f"Input file not found: {source}")

    if source.suffix.lower() not in {".md", ".markdown"}:
        raise ValueError("Input file must be a Markdown file with a .md or .markdown extension.")

    destination = args.output.resolve() if args.output else source.with_suffix(".pdf")
    convert_markdown_to_pdf(source, destination)
    print(f"Created {destination}")


if __name__ == "__main__":
    main()
