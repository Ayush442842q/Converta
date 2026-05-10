# Converta

Converta is a Windows-first offline document converter. It runs locally, keeps files on your machine, and can be packaged as a desktop `.exe`.

The project still includes the original Flask Markdown-to-PDF web UI as a fallback, but the main app is now `desktop_app.py`.

## What It Converts

Built in, without external apps:

| From | To |
| --- | --- |
| Markdown / TXT | PDF, HTML, TXT |
| TXT | DOCX, PDF, HTML, Markdown |
| HTML | PDF, TXT, Markdown |
| DOCX | TXT, HTML, Markdown |
| PDF | TXT |

Optional local tools unlock broader offline conversion:

- **LibreOffice**: best for DOC, DOCX, ODT, RTF, HTML, TXT, and PDF export.
- **Pandoc**: best for Markdown, HTML, DOCX, ODT, RTF, EPUB, TXT, and PDF pipelines.

No cloud conversion is used.

## Run the Windows Desktop App

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe desktop_app.py
```

## Build the Windows EXE

```powershell
.\build_windows.ps1
```

The executable is created at:

```text
dist\Converta\Converta.exe
```

For the widest conversion coverage, install LibreOffice and Pandoc before building or running the app.

## CLI Usage

```powershell
python converter.py sample.md -o sample.pdf
python converter.py report.docx --to txt
python converter.py page.html --to md
```

## Web Fallback

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:8000
```

The web fallback is intentionally smaller than the desktop app and currently focuses on Markdown to PDF.

## Verify Conversion

```powershell
python scripts/check_conversion.py
```

This checks Markdown to PDF, HTML, and TXT using the local conversion engine.

## Project Structure

```text
Converta/
├── app.py                       # Flask fallback app
├── converter.py                 # CLI and legacy Markdown-to-PDF helpers
├── desktop_app.py               # Native Windows desktop app
├── converters/
│   └── document_converter.py    # Offline conversion engine
├── scripts/
│   └── check_conversion.py      # Smoke test
├── templates/                   # Flask fallback templates
├── static/                      # Flask fallback styles
├── build_windows.ps1            # PyInstaller build script
└── requirements.txt
```

## Notes

PDF conversion quality depends on the source document. Text-based PDFs can be extracted to TXT; scanned PDFs need OCR, which is not bundled yet.
