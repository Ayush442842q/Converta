from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from converters import ConversionError, DocumentConverter


class ConversionWorker(QThread):
    progress = Signal(int, str)
    finished = Signal(list, list)

    def __init__(self, converter: DocumentConverter, files: list[Path], output_dir: Path, target_ext: str):
        super().__init__()
        self.converter = converter
        self.files = files
        self.output_dir = output_dir
        self.target_ext = target_ext

    def run(self) -> None:
        successes = []
        failures = []
        total = max(len(self.files), 1)
        for index, source in enumerate(self.files, start=1):
            self.progress.emit(int((index - 1) / total * 100), f"Converting {source.name}")
            destination = self._unique_destination(source)
            try:
                result = self.converter.convert(source, destination)
                successes.append(result)
            except Exception as exc:
                failures.append((source, str(exc)))
            self.progress.emit(int(index / total * 100), f"Finished {source.name}")
        self.finished.emit(successes, failures)

    def _unique_destination(self, source: Path) -> Path:
        candidate = self.output_dir / f"{source.stem}.{self.target_ext}"
        counter = 2
        while candidate.exists():
            candidate = self.output_dir / f"{source.stem}-{counter}.{self.target_ext}"
            counter += 1
        return candidate


class DropList(QListWidget):
    files_dropped = Signal(list)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setSelectionMode(QListWidget.ExtendedSelection)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        paths = [Path(url.toLocalFile()) for url in event.mimeData().urls() if url.isLocalFile()]
        self.files_dropped.emit([path for path in paths if path.is_file()])
        event.acceptProposedAction()


class ConvertaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.converter = DocumentConverter()
        self.files: list[Path] = []
        self.output_dir = Path.home() / "Documents" / "Converta"
        self.worker: ConversionWorker | None = None

        self.setWindowTitle("Converta - Offline Document Converter")
        self.resize(980, 680)
        self._build_ui()
        self._apply_styles()
        self._refresh_status()

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        title = QLabel("Converta")
        title.setObjectName("Title")
        subtitle = QLabel("Offline Windows document conversion. Add files, choose the output format, convert locally.")
        subtitle.setObjectName("Subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        controls = QFrame()
        controls.setObjectName("Panel")
        controls_layout = QHBoxLayout(controls)

        self.add_button = QPushButton("Add files")
        self.add_button.clicked.connect(self.add_files_dialog)
        self.remove_button = QPushButton("Remove selected")
        self.remove_button.clicked.connect(self.remove_selected)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_files)

        self.format_combo = QComboBox()
        for extension in self.converter.supported_extensions():
            self.format_combo.addItem(f".{extension}", extension)
        self.format_combo.setCurrentText(".pdf")

        self.output_button = QPushButton("Output folder")
        self.output_button.clicked.connect(self.choose_output_dir)
        self.convert_button = QPushButton("Convert")
        self.convert_button.setObjectName("PrimaryButton")
        self.convert_button.clicked.connect(self.convert_files)

        controls_layout.addWidget(self.add_button)
        controls_layout.addWidget(self.remove_button)
        controls_layout.addWidget(self.clear_button)
        controls_layout.addStretch()
        controls_layout.addWidget(QLabel("To"))
        controls_layout.addWidget(self.format_combo)
        controls_layout.addWidget(self.output_button)
        controls_layout.addWidget(self.convert_button)
        layout.addWidget(controls)

        self.file_list = DropList()
        self.file_list.files_dropped.connect(self.add_files)
        self.file_list.setObjectName("FileList")
        layout.addWidget(self.file_list, 1)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(140)
        self.log.setObjectName("Log")
        layout.addWidget(self.log)

        self.status = QLabel()
        self.status.setObjectName("Status")
        layout.addWidget(self.status)
        self.setCentralWidget(root)

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background: #101217;
                color: #eef2f7;
                font-family: Segoe UI, Arial, sans-serif;
                font-size: 10pt;
            }
            QLabel#Title {
                font-size: 30px;
                font-weight: 700;
            }
            QLabel#Subtitle, QLabel#Status {
                color: #9aa4b2;
            }
            QFrame#Panel, QListWidget#FileList, QPlainTextEdit#Log {
                background: #171b23;
                border: 1px solid #2b3340;
                border-radius: 8px;
            }
            QListWidget#FileList {
                padding: 10px;
            }
            QPushButton {
                background: #222a36;
                color: #eef2f7;
                border: 1px solid #364253;
                border-radius: 6px;
                padding: 9px 14px;
            }
            QPushButton:hover {
                background: #2b3544;
            }
            QPushButton#PrimaryButton {
                background: #2563eb;
                border-color: #2563eb;
                font-weight: 700;
            }
            QPushButton:disabled {
                color: #6b7280;
                background: #1a1f28;
            }
            QComboBox {
                background: #222a36;
                color: #eef2f7;
                border: 1px solid #364253;
                border-radius: 6px;
                padding: 8px 12px;
                min-width: 96px;
            }
            QProgressBar {
                background: #171b23;
                border: 1px solid #2b3340;
                border-radius: 6px;
                height: 16px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: #22c55e;
                border-radius: 5px;
            }
            """
        )

    def add_files_dialog(self) -> None:
        suffixes = " ".join(f"*.{ext}" for ext in self.converter.supported_extensions())
        filenames, _ = QFileDialog.getOpenFileNames(self, "Choose documents", str(Path.home()), f"Documents ({suffixes})")
        self.add_files([Path(name) for name in filenames])

    def add_files(self, paths: list[Path]) -> None:
        known = {path.resolve() for path in self.files}
        added = 0
        for path in paths:
            resolved = path.resolve()
            if resolved in known:
                continue
            if self.converter.normalize_extension(path.suffix) not in self.converter.FORMATS:
                self._append_log(f"Skipped unsupported file: {path.name}")
                continue
            self.files.append(resolved)
            known.add(resolved)
            added += 1
        if added:
            self.render_files()
            self._append_log(f"Added {added} file(s).")

    def render_files(self) -> None:
        self.file_list.clear()
        for path in self.files:
            item = QListWidgetItem(f"{path.name}    {path.parent}")
            item.setData(Qt.UserRole, str(path))
            self.file_list.addItem(item)
        self._refresh_status()

    def remove_selected(self) -> None:
        selected = {Path(item.data(Qt.UserRole)) for item in self.file_list.selectedItems()}
        self.files = [path for path in self.files if path not in selected]
        self.render_files()

    def clear_files(self) -> None:
        self.files.clear()
        self.render_files()

    def choose_output_dir(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Choose output folder", str(self.output_dir))
        if folder:
            self.output_dir = Path(folder)
            self._refresh_status()

    def convert_files(self) -> None:
        if not self.files:
            QMessageBox.information(self, "No files", "Add at least one document first.")
            return

        target_ext = self.format_combo.currentData()
        unsupported = [
            path.name
            for path in self.files
            if not self.converter.can_convert(path.suffix, target_ext)
        ]
        if unsupported:
            message = "These files need LibreOffice or Pandoc for the selected output:\n\n"
            message += "\n".join(unsupported[:8])
            if len(unsupported) > 8:
                message += f"\n...and {len(unsupported) - 8} more"
            QMessageBox.warning(self, "Converter unavailable", message)
            return

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.convert_button.setDisabled(True)
        self.progress.setValue(0)
        self.worker = ConversionWorker(self.converter, list(self.files), self.output_dir, target_ext)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_progress(self, percent: int, message: str) -> None:
        self.progress.setValue(percent)
        self.status.setText(message)

    def on_finished(self, successes: list, failures: list) -> None:
        self.convert_button.setDisabled(False)
        self.progress.setValue(100)
        for result in successes:
            self._append_log(f"OK: {result.source.name} -> {result.destination.name} ({result.engine})")
        for source, error in failures:
            self._append_log(f"FAILED: {source.name}: {error}")
        self.status.setText(f"Done. {len(successes)} converted, {len(failures)} failed. Output: {self.output_dir}")
        if failures:
            QMessageBox.warning(self, "Completed with errors", f"{len(successes)} converted, {len(failures)} failed.")
        else:
            QMessageBox.information(self, "Conversion complete", f"Converted {len(successes)} file(s).")

    def _append_log(self, message: str) -> None:
        self.log.appendPlainText(message)

    def _refresh_status(self) -> None:
        notes = " | ".join(self.converter.explain_availability())
        self.status.setText(f"{len(self.files)} file(s). Output: {self.output_dir}. {notes}")


def main() -> int:
    app = QApplication(sys.argv)
    window = ConvertaWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ConversionError as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1)
