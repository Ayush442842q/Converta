from __future__ import annotations

import tempfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from converters import DocumentConverter


def main() -> None:
    converter = DocumentConverter()
    with tempfile.TemporaryDirectory(prefix="converta-check-") as temp_dir:
        root = Path(temp_dir)
        source = root / "sample.md"
        pdf = root / "sample.pdf"
        html = root / "sample.html"
        text = root / "sample.txt"
        source.write_text("# Converta\n\nOffline conversion check.\n", encoding="utf-8")

        for destination in (pdf, html, text):
            result = converter.convert(source, destination)
            if not result.destination.exists() or result.destination.stat().st_size == 0:
                raise RuntimeError(f"Output was not created: {destination}")
            print(f"OK {result.source.name} -> {result.destination.name} via {result.engine}")

        print("Availability:")
        for note in converter.explain_availability():
            print(f"- {note}")


if __name__ == "__main__":
    main()
