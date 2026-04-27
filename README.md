# Markdown to PDF Converter

Small local web app for turning Markdown into a PDF from your browser.

## Setup

```bash
pip install -r requirements.txt
```

## Run the website

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:8000
```

## What it does

- paste Markdown into the editor
- upload a `.md` or `.markdown` file
- optionally choose the output filename
- download the generated PDF directly from the page

## Optional CLI

The original CLI still works:

```bash
python converter.py input.md
python converter.py input.md -o output.pdf
```
