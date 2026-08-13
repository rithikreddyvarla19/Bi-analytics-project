from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data"
OUTPUT_ROOT = PROJECT_ROOT / "outputs"


def configure_logging(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_run_metadata(
    metadata: dict[str, Any], file_name: str = "pipeline_run_metadata.json"
) -> Path:
    ensure_dir(OUTPUT_ROOT / "observability")
    output_path = OUTPUT_ROOT / "observability" / file_name
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        **metadata,
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path
