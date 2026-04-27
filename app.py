from __future__ import annotations

import zipfile
from io import BytesIO
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, send_file, url_for

from converter import convert_markdown_text_to_pdf_bytes


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024   # 50 MB for batch
app.secret_key = "markdown-to-pdf-local-app"


def extract_markdown_text() -> tuple[str, str]:
    uploaded_file = request.files.get("markdown_file")
    pasted_text = request.form.get("markdown_text", "").strip()
    filename = request.form.get("output_name", "").strip()

    if uploaded_file and uploaded_file.filename:
        markdown_text = uploaded_file.read().decode("utf-8")
        stem = Path(uploaded_file.filename).stem or "document"
        return markdown_text, filename or stem

    if pasted_text:
        return pasted_text, filename or "document"

    raise ValueError("Please upload a Markdown file or paste Markdown into the editor.")


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/convert")
def convert():
    try:
        markdown_text, output_name = extract_markdown_text()
        pdf_bytes = convert_markdown_text_to_pdf_bytes(markdown_text, title=output_name)
    except Exception as exc:
        flash(str(exc), "error")
        return redirect(url_for("index"))

    buffer = BytesIO(pdf_bytes)
    download_name = f"{Path(output_name).stem or 'document'}.pdf"
    return send_file(buffer, as_attachment=True, download_name=download_name, mimetype="application/pdf")


@app.post("/convert-batch")
def convert_batch():
    """Accept multiple markdown files, convert each to PDF, return a ZIP."""
    files = request.files.getlist("markdown_files")
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

    successful = [(name, data) for name, data, err in results if data]
    errors     = [(name, err)  for name, data, err in results if err]

    if not successful:
        return {"error": "All files failed to convert", "details": errors}, 422

    # Single file → return PDF directly (no zip overhead)
    if len(successful) == 1:
        name, pdf_bytes = successful[0]
        return send_file(
            BytesIO(pdf_bytes),
            as_attachment=True,
            download_name=name,
            mimetype="application/pdf",
        )

    # Multiple files → ZIP
    zip_buf = BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, pdf_bytes in successful:
            zf.writestr(name, pdf_bytes)

    zip_buf.seek(0)
    return send_file(
        zip_buf,
        as_attachment=True,
        download_name="converted_pdfs.zip",
        mimetype="application/zip",
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)
