from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data"


def run_pandas() -> None:
    files = sorted((DATA_ROOT / "streaming" / "processed").glob("*.jsonl"))
    if not files:
        return

    events = pd.concat((pd.read_json(f, lines=True) for f in files), ignore_index=True)
    if events.empty:
        return

    events["event_ts"] = pd.to_datetime(events["event_ts"], errors="coerce")
    events["event_hour"] = events["event_ts"].dt.floor("h")
    events["event_date"] = events["event_ts"].dt.date.astype(str)

    hourly = (
        events.groupby(["event_hour", "channel", "event_type"], as_index=False)
        .agg(event_count=("event_id", "count"), sessions=("session_id", "nunique"), distinct_products=("product_id", "nunique"))
    )

    product_activity = (
        events.groupby(["event_date", "product_id", "event_type"], as_index=False)
        .agg(event_count=("event_id", "count"))
    )

    (DATA_ROOT / "gold" / "streaming_hourly_activity").mkdir(parents=True, exist_ok=True)
    (DATA_ROOT / "gold" / "streaming_product_activity").mkdir(parents=True, exist_ok=True)

    hourly.to_parquet(DATA_ROOT / "gold" / "streaming_hourly_activity", index=False, partition_cols=["event_hour"])
    product_activity.to_parquet(DATA_ROOT / "gold" / "streaming_product_activity", index=False, partition_cols=["event_date"])


def run_spark() -> None:
    from pyspark.sql import SparkSession, functions as F

    spark = (
        SparkSession.builder.appName("streaming-microbatch-aggregator")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )

    source = str(DATA_ROOT / "streaming" / "processed" / "*.jsonl")
    events = spark.read.json(source)

    if events.rdd.isEmpty():
        spark.stop()
        return

    hourly = (
        events.withColumn("event_ts", F.to_timestamp("event_ts"))
        .withColumn("event_hour", F.date_trunc("hour", F.col("event_ts")))
        .groupBy("event_hour", "channel", "event_type")
        .agg(F.count("event_id").alias("event_count"), F.countDistinct("session_id").alias("sessions"), F.countDistinct("product_id").alias("distinct_products"))
    )

    product_activity = (
        events.withColumn("event_ts", F.to_timestamp("event_ts"))
        .groupBy(F.to_date("event_ts").alias("event_date"), "product_id", "event_type")
        .agg(F.count("event_id").alias("event_count"))
    )

    hourly.write.mode("overwrite").partitionBy("event_hour").parquet(str(DATA_ROOT / "gold" / "streaming_hourly_activity"))
    product_activity.write.mode("overwrite").partitionBy("event_date").parquet(str(DATA_ROOT / "gold" / "streaming_product_activity"))
    spark.stop()


def main() -> None:
    try:
        run_spark()
    except Exception:
        run_pandas()


if __name__ == "__main__":
    main()
