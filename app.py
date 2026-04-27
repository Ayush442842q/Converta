from __future__ import annotations

import zipfile
from io import BytesIO
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, send_file, url_for, abort

from converter import convert_markdown_text_to_pdf_bytes


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024   # 50 MB for batch
app.secret_key = "converta-local-app"


# Central Registry of all tools
TOOLS = [
    {
        "id": "markdown-to-pdf",
        "name": "Markdown to PDF",
        "description": "Convert Markdown text files to beautifully styled PDF documents.",
        "icon": "MD",
        "category": "Document Conversions",
        "accept": ".md,.markdown,text/markdown",
        "status": "active"
    },
    {
        "id": "pdf-to-word",
        "name": "PDF to Word",
        "description": "Easily convert your PDF files into easy to edit DOCX documents.",
        "icon": "PDF",
        "category": "PDF Conversions",
        "accept": ".pdf,application/pdf",
        "status": "coming_soon"
    },
    {
        "id": "word-to-pdf",
        "name": "Word to PDF",
        "description": "Make DOC and DOCX files easy to read by converting them to PDF.",
        "icon": "DOC",
        "category": "Convert to PDF",
        "accept": ".doc,.docx",
        "status": "coming_soon"
    },
    {
        "id": "pdf-to-excel",
        "name": "PDF to Excel",
        "description": "Pull data straight from PDFs into Excel spreadsheets.",
        "icon": "PDF",
        "category": "PDF Conversions",
        "accept": ".pdf,application/pdf",
        "status": "coming_soon"
    },
    {
        "id": "jpg-to-pdf",
        "name": "JPG to PDF",
        "description": "Convert JPG images to PDF in seconds.",
        "icon": "JPG",
        "category": "Convert to PDF",
        "accept": ".jpg,.jpeg,image/jpeg",
        "status": "coming_soon"
    },
    {
        "id": "merge-pdf",
        "name": "Merge PDF",
        "description": "Combine PDFs in the order you want with the easiest PDF merger.",
        "icon": "MRG",
        "category": "PDF Tools",
        "accept": ".pdf,application/pdf",
        "status": "coming_soon"
    }
]

# Group tools by category for the dashboard
CATEGORIES = [
    "PDF Conversions", 
    "Convert to PDF", 
    "Image Conversions", 
    "Document Conversions", 
    "PDF Tools"
]

def get_tool_by_id(tool_id):
    for tool in TOOLS:
        if tool["id"] == tool_id:
            return tool
    return None


@app.get("/")
def index():
    # Group tools by category
    tools_by_category = {cat: [] for cat in CATEGORIES}
    for tool in TOOLS:
        if tool["category"] in tools_by_category:
            tools_by_category[tool["category"]].append(tool)
    
    return render_template("index.html", categories=CATEGORIES, tools_by_category=tools_by_category)


@app.get("/tool/<tool_id>")
def tool_page(tool_id):
    tool = get_tool_by_id(tool_id)
    if not tool:
        abort(404)
        
    return render_template("tool.html", tool=tool)


# ---------------------------------------------------------------------------
# CONVERTER BACKENDS
# ---------------------------------------------------------------------------

@app.post("/api/convert/markdown-to-pdf")
def convert_markdown_to_pdf_batch():
    """Accept multiple markdown files, convert each to PDF, return a ZIP."""
    files = request.files.getlist("files")
    valid = [f for f in files if f and f.filename]

    if not valid:
        return {"error": "No files provided"}, 400

    results = []   # list of (pdf_name, pdf_bytes, error_msg)

    for f in valid:
        stem = Path(f.filename).stem or "document"
        try:
            md_text = f.read().decode("utf-8")
            pdf_bytes = convert_markdown_text_to_pdf_bytes(md_text, title=stem)
            results.append((f"{stem}.pdf", pdf_bytes, None))
        except Exception as exc:
            results.append((f"{stem}.pdf", None, str(exc)))

    return handle_batch_response(results)

# ---------------------------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------------------------

def handle_batch_response(results):
    """Takes a list of (filename, file_bytes, error) and returns a file or zip response."""
    successful = [(name, data) for name, data, err in results if data]
    errors     = [(name, err)  for name, data, err in results if err]

    if not successful:
        return {"error": "All files failed to convert", "details": errors}, 422

    # Single file → return file directly (no zip overhead)
    if len(successful) == 1:
        name, file_bytes = successful[0]
        return send_file(
            BytesIO(file_bytes),
            as_attachment=True,
            download_name=name
        )

    # Multiple files → ZIP
    zip_buf = BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, file_bytes in successful:
            zf.writestr(name, file_bytes)

    zip_buf.seek(0)
    return send_file(
        zip_buf,
        as_attachment=True,
        download_name="converta_files.zip",
        mimetype="application/zip",
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)
