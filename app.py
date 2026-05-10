from __future__ import annotations

import os
import zipfile
from io import BytesIO
from pathlib import Path

from flask import Flask, abort, render_template, request, send_file
from werkzeug.utils import secure_filename

from converter import convert_markdown_text_to_pdf_bytes


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
app.secret_key = os.environ.get("SECRET_KEY", "converta-local-dev-key")

ALLOWED_MARKDOWN_EXTENSIONS = {".md", ".markdown", ".txt"}


TOOLS = [
    {
        "id": "markdown-to-pdf",
        "name": "Markdown to PDF",
        "description": "Convert Markdown text files to polished PDF documents.",
        "icon": "MD",
        "category": "Document Conversions",
        "accept": ".md,.markdown,.txt,text/markdown,text/plain",
        "status": "active",
    },
    {
        "id": "pdf-to-word",
        "name": "PDF to Word",
        "description": "Convert PDF files into editable DOCX documents.",
        "icon": "PDF",
        "category": "PDF Conversions",
        "accept": ".pdf,application/pdf",
        "status": "coming_soon",
    },
    {
        "id": "word-to-pdf",
        "name": "Word to PDF",
        "description": "Turn DOC and DOCX files into shareable PDFs.",
        "icon": "DOC",
        "category": "Convert to PDF",
        "accept": ".doc,.docx",
        "status": "coming_soon",
    },
    {
        "id": "pdf-to-excel",
        "name": "PDF to Excel",
        "description": "Pull data from PDFs into spreadsheets.",
        "icon": "PDF",
        "category": "PDF Conversions",
        "accept": ".pdf,application/pdf",
        "status": "coming_soon",
    },
    {
        "id": "jpg-to-pdf",
        "name": "JPG to PDF",
        "description": "Convert JPG images to PDF in seconds.",
        "icon": "JPG",
        "category": "Convert to PDF",
        "accept": ".jpg,.jpeg,image/jpeg",
        "status": "coming_soon",
    },
    {
        "id": "merge-pdf",
        "name": "Merge PDF",
        "description": "Combine PDFs in the order you want.",
        "icon": "MRG",
        "category": "PDF Tools",
        "accept": ".pdf,application/pdf",
        "status": "coming_soon",
    },
]

CATEGORIES = [
    "PDF Conversions",
    "Convert to PDF",
    "Image Conversions",
    "Document Conversions",
    "PDF Tools",
]


def get_tool_by_id(tool_id: str) -> dict | None:
    return next((tool for tool in TOOLS if tool["id"] == tool_id), None)


def validate_markdown_filename(filename: str) -> None:
    if Path(filename).suffix.lower() not in ALLOWED_MARKDOWN_EXTENSIONS:
        raise ValueError("Only .md, .markdown, and .txt files are supported.")


def pdf_download_name(name: str, fallback: str = "document") -> str:
    safe_name = secure_filename(name or fallback) or fallback
    return f"{Path(safe_name).stem or fallback}.pdf"


def unique_archive_name(name: str, used_names: set[str]) -> str:
    path = Path(name)
    stem = path.stem or "document"
    suffix = path.suffix or ".pdf"
    candidate = f"{stem}{suffix}"
    counter = 2
    while candidate in used_names:
        candidate = f"{stem}-{counter}{suffix}"
        counter += 1
    used_names.add(candidate)
    return candidate


@app.get("/")
def index():
    tools_by_category = {cat: [] for cat in CATEGORIES}
    for tool in TOOLS:
        if tool["category"] in tools_by_category:
            tools_by_category[tool["category"]].append(tool)

    return render_template(
        "index.html",
        categories=CATEGORIES,
        tools_by_category=tools_by_category,
    )


@app.get("/tool/<tool_id>")
def tool_page(tool_id: str):
    tool = get_tool_by_id(tool_id)
    if not tool:
        abort(404)

    return render_template("tool.html", tool=tool)


@app.post("/api/convert/markdown-to-pdf")
def convert_markdown_to_pdf_batch():
    markdown_text = request.form.get("markdown_text", "").strip()
    if markdown_text:
        output_name = request.form.get("output_name", "document")
        pdf_bytes = convert_markdown_text_to_pdf_bytes(
            markdown_text,
            title=Path(output_name).stem or "document",
        )
        return send_file(
            BytesIO(pdf_bytes),
            as_attachment=True,
            download_name=pdf_download_name(output_name),
            mimetype="application/pdf",
        )

    files = [f for f in request.files.getlist("files") if f and f.filename]
    if not files:
        return {"error": "Add Markdown text or upload at least one file."}, 400

    results = []
    for file_storage in files:
        filename = secure_filename(file_storage.filename)
        pdf_name = pdf_download_name(filename)
        try:
            validate_markdown_filename(filename)
            markdown_source = file_storage.read().decode("utf-8")
            pdf_bytes = convert_markdown_text_to_pdf_bytes(
                markdown_source,
                title=Path(filename).stem or "document",
            )
            results.append((pdf_name, pdf_bytes, None))
        except UnicodeDecodeError:
            results.append((pdf_name, None, "File is not valid UTF-8 text."))
        except Exception as exc:
            results.append((pdf_name, None, str(exc)))

    return handle_batch_response(results)


def handle_batch_response(results: list[tuple[str, bytes | None, str | None]]):
    successful = [(name, data) for name, data, err in results if data]
    errors = [(name, err) for name, data, err in results if err]

    if not successful:
        return {"error": "All files failed to convert.", "details": errors}, 422

    if len(successful) == 1 and not errors:
        name, file_bytes = successful[0]
        return send_file(
            BytesIO(file_bytes),
            as_attachment=True,
            download_name=name,
            mimetype="application/pdf",
        )

    used_names: set[str] = set()
    zip_buf = BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, file_bytes in successful:
            zf.writestr(unique_archive_name(name, used_names), file_bytes)
        if errors:
            lines = [f"{name}: {err}" for name, err in errors]
            zf.writestr("conversion-errors.txt", "\n".join(lines))

    zip_buf.seek(0)
    return send_file(
        zip_buf,
        as_attachment=True,
        download_name="converta_files.zip",
        mimetype="application/zip",
    )


@app.get("/health")
def health():
    active_tools = [tool["id"] for tool in TOOLS if tool["status"] == "active"]
    return {"status": "ok", "active_tools": active_tools}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)
