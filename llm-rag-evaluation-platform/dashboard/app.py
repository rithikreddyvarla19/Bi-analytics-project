"""Streamlit monitoring dashboard."""

from __future__ import annotations

import streamlit as st

from dashboard.data_access import load_evaluation_results, load_feedback

st.set_page_config(page_title="Knowledge Assistant Monitoring", layout="wide")
st.title("Knowledge Assistant Monitoring")

evaluation_df = load_evaluation_results()
feedback_df = load_feedback()

metric_columns = st.columns(6)
metrics = [
    "top_3_accuracy",
    "faithfulness",
    "hallucination_rate",
    "calibration_score",
    "answer_relevancy",
    "context_recall",
]
for metric in metrics:
    if metric not in evaluation_df:
        evaluation_df[metric] = 0.0
for column, metric in zip(metric_columns, metrics, strict=True):
    value = float(evaluation_df[metric].mean()) if metric in evaluation_df else 0.0
    column.metric(metric.replace("_", " ").title(), f"{value:.2%}")

left, right = st.columns([2, 1])
with left:
    st.subheader("Prompt and Model Comparison")
    prompt_metrics = evaluation_df.groupby("prompt_id", as_index=False)[metrics].mean()
    st.bar_chart(prompt_metrics.set_index("prompt_id"))

with right:
    st.subheader("Latency")
    if "latency_ms" in evaluation_df:
        st.line_chart(evaluation_df["latency_ms"])
    else:
        st.info("No latency measurements have been logged yet.")

st.subheader("Hallucination Trend")
if "hallucination_rate" in evaluation_df:
    st.line_chart(evaluation_df["hallucination_rate"])

st.subheader("Calibration")
if "calibration_score" in evaluation_df:
    st.line_chart(evaluation_df["calibration_score"])

st.subheader("User Feedback")
if feedback_df.empty:
    st.info("No feedback events yet.")
else:
    st.dataframe(feedback_df.sort_values("created_at", ascending=False), use_container_width=True)
