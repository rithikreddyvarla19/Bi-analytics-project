"""Production-oriented loaders for raw enterprise documents.

The loaders keep dependencies optional. PDF extraction uses pypdf when it is
installed, CSV and text ingestion use the Python standard library, and every
document receives deterministic identifiers and checksums for incremental
processing.
"""

from __future__ import annotations

import csv
import hashlib
import logging
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

logger = logging.getLogger(__name__)


SUPPORTED_EXTENSIONS = {".txt", ".md", ".csv", ".pdf"}


@dataclass(frozen=True)
class RawDocument:
    """A normalized document emitted by source-specific loaders."""

    id: str
    text: str
    source_path: str
    source_type: str
    checksum: str
    metadata: dict[str, str | int | float | bool] = field(default_factory=dict)


class Loader(Protocol):
    """Source-specific loader interface."""

    extensions: set[str]

    def load(self, path: Path) -> list[RawDocument]:
        """Load one path into one or more normalized documents."""


def _checksum(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _document_id(path: Path, checksum: str, suffix: str = "") -> str:
    digest = hashlib.sha1(f"{path.as_posix()}::{checksum}::{suffix}".encode()).hexdigest()
    return digest[:16]


class TextDocumentLoader:
    """Load plain text and markdown files."""

    extensions = {".txt", ".md"}

    def load(self, path: Path) -> list[RawDocument]:
        content = path.read_bytes()
        text = content.decode("utf-8", errors="replace")
        checksum = _checksum(content)
        return [
            RawDocument(
                id=_document_id(path, checksum),
                text=text,
                source_path=str(path),
                source_type=path.suffix.lower().lstrip("."),
                checksum=checksum,
                metadata={"filename": path.name, "source_id": path.stem},
            )
        ]


class CSVDocumentLoader:
    """Load CSV rows as row-level documents with column labels preserved."""

    extensions = {".csv"}

    def load(self, path: Path) -> list[RawDocument]:
        content = path.read_bytes()
        checksum = _checksum(content)
        decoded = content.decode("utf-8-sig", errors="replace").splitlines()
        reader = csv.DictReader(decoded)

        documents: list[RawDocument] = []
        for row_number, row in enumerate(reader, start=1):
            fields = [f"{key}: {value}" for key, value in row.items() if value not in (None, "")]
            text = "\n".join(fields).strip()
            if not text:
                continue
            documents.append(
                RawDocument(
                    id=_document_id(path, checksum, suffix=str(row_number)),
                    text=text,
                    source_path=str(path),
                    source_type="csv",
                    checksum=checksum,
                    metadata={"filename": path.name, "source_id": path.stem, "row_number": row_number},
                )
            )
        return documents


class PDFDocumentLoader:
    """Load PDFs with pypdf, returning one document per page."""

    extensions = {".pdf"}

    def load(self, path: Path) -> list[RawDocument]:
        try:
            from pypdf import PdfReader
        except ImportError as exc:  # pragma: no cover - depends on optional extra
            raise RuntimeError("PDF ingestion requires pypdf. Install the production dependencies.") from exc

        content = path.read_bytes()
        checksum = _checksum(content)
        reader = PdfReader(str(path))
        documents: list[RawDocument] = []
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if not text.strip():
                continue
            documents.append(
                RawDocument(
                    id=_document_id(path, checksum, suffix=f"page-{page_number}"),
                    text=text,
                    source_path=str(path),
                    source_type="pdf",
                    checksum=checksum,
                    metadata={"filename": path.name, "source_id": path.stem, "page_number": page_number},
                )
            )
        return documents


class DocumentIngestor:
    """Dispatch files to source-specific loaders."""

    def __init__(self, loaders: Iterable[Loader] | None = None) -> None:
        self.loaders = list(loaders or [TextDocumentLoader(), CSVDocumentLoader(), PDFDocumentLoader()])
        self._by_extension = {
            extension: loader for loader in self.loaders for extension in loader.extensions
        }

    def discover(self, input_path: str | Path) -> list[Path]:
        path = Path(input_path)
        if path.is_file():
            return [path] if path.suffix.lower() in self._by_extension else []
        if not path.exists():
            raise FileNotFoundError(f"Input path does not exist: {path}")
        return sorted(
            candidate
            for candidate in path.rglob("*")
            if candidate.is_file() and candidate.suffix.lower() in self._by_extension
        )

    def load_path(self, input_path: str | Path, *, fail_fast: bool = False) -> list[RawDocument]:
        return list(self.iter_path(input_path, fail_fast=fail_fast))

    def iter_path(self, input_path: str | Path, *, fail_fast: bool = False) -> Iterable[RawDocument]:
        for path in self.discover(input_path):
            loader = self._by_extension[path.suffix.lower()]
            try:
                yield from loader.load(path)
            except Exception:
                logger.exception("Failed to load %s", path)
                if fail_fast:
                    raise
