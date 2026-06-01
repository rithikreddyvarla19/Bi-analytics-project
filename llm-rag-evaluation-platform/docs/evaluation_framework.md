# Evaluation Framework

The evaluation package provides deterministic metrics suitable for CI and scheduled model validation.

## Metrics

- Top-3 answer accuracy: whether any expected source appears in the top three retrieved contexts.
- Faithfulness: percentage of generated answer terms supported by retrieved context.
- Hallucination rate: inverse of faithfulness.
- Calibration score: how closely retrieval confidence tracks answer correctness.
- Context precision: fraction of retrieved source IDs that match expected source IDs.
- Context recall: coverage of expected source IDs and expected context content.
- Answer relevancy: lexical overlap between the question, expected answer, and generated answer.

Prompt experiments and hyperparameter tuning use these metrics to compare prompt templates, few-shot examples, retriever `top_k`, model names, and temperature settings.

## Ground Truth Validation

Ground-truth records require:

- `id`
- `question`
- `expected_answer`
- `expected_contexts` or `expected_source_ids`

Use:

```bash
python scripts/run_evaluation.py \
  --dataset sample_datasets/ground_truth/rag_eval.csv \
  --index artifacts/vector_index \
  --output artifacts/evaluation/results.csv \
  --baseline-top3 0.60 \
  --log-mlflow
```
