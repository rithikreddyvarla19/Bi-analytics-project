from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

try:
    from common import DATA_ROOT, configure_logging, ensure_dir
except ModuleNotFoundError:
    from scripts.common import DATA_ROOT, configure_logging, ensure_dir

logger = configure_logging("streaming_simulator")


def _load_products() -> list[str]:
    products_path = DATA_ROOT / "raw" / "products.csv"
    if not products_path.exists():
        raise FileNotFoundError("Run scripts/generate_data.py before streaming simulation")
    return pd.read_csv(products_path)["product_id"].tolist()


def _create_event(event_id: int, product_ids: list[str], event_time: datetime) -> dict[str, object]:
    return {
        "event_id": f"STR{event_id:010d}",
        "event_ts": event_time.isoformat(),
        "event_type": np.random.choice(
            ["inventory_update", "product_view", "add_to_cart", "purchase"],
            p=[0.2, 0.45, 0.2, 0.15],
        ),
        "product_id": np.random.choice(product_ids),
        "channel": np.random.choice(["web", "mobile", "store"]),
        "region": np.random.choice(["Northeast", "Southeast", "Midwest", "West"]),
        "delta_qty": int(np.random.randint(-3, 6)),
        "session_id": f"S{np.random.randint(1, 4000):07d}",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate file-based micro-batch streaming events")
    parser.add_argument("--batches", type=int, default=4)
    parser.add_argument("--events-per-batch", type=int, default=1200)
    args = parser.parse_args()

    incoming_dir = ensure_dir(DATA_ROOT / "streaming" / "incoming")
    processed_dir = ensure_dir(DATA_ROOT / "streaming" / "processed")
    product_ids = _load_products()

    event_counter = 1
    base_ts = datetime.utcnow() - timedelta(hours=6)

    for batch_idx in range(args.batches):
        batch_name = f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{batch_idx:02d}.jsonl"
        batch_path = incoming_dir / batch_name
        with batch_path.open("w", encoding="utf-8") as handle:
            for _ in range(args.events_per_batch):
                event = _create_event(
                    event_counter, product_ids, base_ts + timedelta(seconds=event_counter * 3)
                )
                handle.write(json.dumps(event) + "\n")
                event_counter += 1

        archived_path = processed_dir / batch_name
        batch_path.replace(archived_path)
        logger.info("Generated and archived streaming batch %s", archived_path.name)


if __name__ == "__main__":
    main()
