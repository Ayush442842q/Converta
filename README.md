# Converta 🔄

> **Every file conversion tool you need — in one place.**  
> A self-hosted, open-source alternative to iLovePDF / Smallpdf. Built with Python + Flask.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?style=flat-square&logo=flask)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

---

## ✨ Features

- 🖥️ Beautiful dark-mode dashboard — iLovePDF-style tool grid
- 📦 Multi-file queue with drag & drop, batch convert & ZIP download
- ⚡ Live Markdown preview editor
- 🎨 5 themes, customizable layout & typography
- 🔒 Fully local — no files ever leave your machine

---

## 🛠️ Converter Roadmap

### 📄 PDF Conversions
| # | Tool | Status |
|---|------|--------|
| 1 | Markdown → PDF | ✅ Done |
| 2 | PDF → Word (.docx) | 🔜 Coming |
| 3 | PDF → Excel (.xlsx) | 🔜 Coming |
| 4 | PDF → PowerPoint (.pptx) | 🔜 Coming |
| 5 | PDF → TXT | 🔜 Coming |
| 6 | PDF → HTML | 🔜 Coming |
| 7 | PDF → JPG | 🔜 Coming |
| 8 | PDF → PNG | 🔜 Coming |
| 9 | PDF → SVG | 🔜 Coming |
| 10 | PDF → CSV | 🔜 Coming |
| 11 | PDF → EPUB | 🔜 Coming |

### 📥 Convert to PDF
| # | Tool | Status |
|---|------|--------|
| 12 | Word → PDF | 🔜 Coming |
| 13 | Excel → PDF | 🔜 Coming |
| 14 | PowerPoint → PDF | 🔜 Coming |
| 15 | HTML → PDF | 🔜 Coming |
| 16 | TXT → PDF | 🔜 Coming |
| 17 | Image → PDF | 🔜 Coming |
| 18 | CSV → PDF | 🔜 Coming |
| 19 | EPUB → PDF | 🔜 Coming |

### 🖼️ Image Conversions
| # | Tool | Status |
|---|------|--------|
| 20 | JPG → PNG | 🔜 Coming |
| 21 | PNG → JPG | 🔜 Coming |
| 22 | JPG → WEBP | 🔜 Coming |
| 23 | PNG → WEBP | 🔜 Coming |
| 24 | WEBP → PNG | 🔜 Coming |
| 25 | WEBP → JPG | 🔜 Coming |
| 26 | BMP → JPG | 🔜 Coming |
| 27 | BMP → PNG | 🔜 Coming |
| 28 | GIF → PNG | 🔜 Coming |
| 29 | GIF → MP4 | 🔜 Coming |
| 30 | PNG → SVG | 🔜 Coming |
| 31 | SVG → PNG | 🔜 Coming |
| 32 | PNG → ICO | 🔜 Coming |
| 33 | TIFF → JPG | 🔜 Coming |
| 34 | HEIC → JPG | 🔜 Coming |

### 📝 Document Conversions
| # | Tool | Status |
|---|------|--------|
| 35 | Word → TXT | 🔜 Coming |
| 36 | Word → HTML | 🔜 Coming |
| 37 | Word → Markdown | 🔜 Coming |
| 38 | Excel → CSV | 🔜 Coming |
| 39 | CSV → Excel | 🔜 Coming |
| 40 | HTML → Markdown | 🔜 Coming |
| 41 | Markdown → HTML | 🔜 Coming |
| 42 | TXT → Word | 🔜 Coming |

### 🔧 PDF Tools (Bonus)
| # | Tool | Status |
|---|------|--------|
| 43 | Merge PDFs | 🔜 Coming |
| 44 | Split PDF | 🔜 Coming |
| 45 | Compress PDF | 🔜 Coming |
| 46 | Rotate PDF | 🔜 Coming |
| 47 | Watermark PDF | 🔜 Coming |
| 48 | OCR PDF | 🔜 Coming |

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/Ayush442842q/Converta.git
cd Converta

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
# Open http://127.0.0.1:8000
```

---

## 📦 Dependencies

```
flask
markdown
xhtml2pdf
Pillow
pypdf
python-docx
mammoth
openpyxl
```

---

## 📁 Project Structure

```
converta/
├── app.py              # Flask app + all routes
├── converter.py        # Markdown → PDF engine
├── converters/         # Individual converter modules (one per tool)
├── templates/
│   ├── index.html      # Homepage dashboard
│   └── tool.html       # Per-tool upload/queue UI
├── static/
│   ├── styles.css      # Main styles + themes
│   └── settings.css    # Settings panel styles
├── requirements.txt
└── README.md
```

---

## 📜 License

MIT — free to use, modify, and distribute.
