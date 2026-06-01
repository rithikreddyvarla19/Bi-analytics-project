"""Prompt registry and formatting helpers."""

from __future__ import annotations

from dataclasses import dataclass

from rag_pipeline.vector_store import SearchResult


@dataclass(frozen=True)
class PromptTemplate:
    id: str
    name: str
    template: str


DEFAULT_PROMPTS = {
    "enterprise_cited": PromptTemplate(
        id="enterprise_cited",
        name="Enterprise cited answer",
        template=(
            "You are an enterprise RAG assistant. Answer the question using only the "
            "provided context. Cite sources inline using bracketed source numbers such "
            "as [S1]. If the answer is not in the context, say that the available "
            "sources do not contain enough information.\n\n"
            "Question:\n{question}\n\n"
            "Context:\n{context}\n\n"
            "Answer:"
        ),
    ),
    "risk_averse": PromptTemplate(
        id="risk_averse",
        name="Risk-averse compliance answer",
        template=(
            "You are a compliance-sensitive assistant. Prefer precise, short answers. "
            "Do not infer beyond the retrieved evidence. Include citations for every "
            "material claim.\n\nQuestion: {question}\n\nEvidence:\n{context}\n\nAnswer:"
        ),
    ),
    "executive": PromptTemplate(
        id="executive",
        name="Executive summary answer",
        template=(
            "Use the evidence to answer for an executive audience. Lead with the answer, "
            "then give two to four concise supporting details with citations.\n\n"
            "Question: {question}\n\nEvidence:\n{context}\n\nAnswer:"
        ),
    ),
    "few_shot_technical": PromptTemplate(
        id="few_shot_technical",
        name="Few-shot technical-document answer",
        template=(
            "You are a technical knowledge assistant answering from indexed product, "
            "operations, and policy documentation. Follow the examples, use only the "
            "retrieved evidence, and cite every factual claim.\n\n"
            "Example 1\n"
            "Question: What blocks a release when model quality drops?\n"
            "Answer: A production release is blocked when faithfulness falls below the "
            "approved threshold, and remediation must be approved by the model risk owner. [S1]\n\n"
            "Example 2\n"
            "Question: How should unsupported claims be handled?\n"
            "Answer: Unsupported claims should be flagged for review and used to improve prompts, "
            "retrieval settings, or training data quality. [S1]\n\n"
            "Question: {question}\n\nEvidence:\n{context}\n\nAnswer:"
        ),
    ),
}


class PromptRegistry:
    """In-memory prompt registry with explicit prompt IDs for experiments."""

    def __init__(self, prompts: dict[str, PromptTemplate] | None = None) -> None:
        self.prompts = dict(prompts or DEFAULT_PROMPTS)

    def get(self, prompt_id: str) -> PromptTemplate:
        try:
            return self.prompts[prompt_id]
        except KeyError as exc:
            raise ValueError(f"Unknown prompt_id: {prompt_id}") from exc

    def render(self, prompt_id: str, question: str, results: list[SearchResult]) -> str:
        context = format_context(results)
        return self.get(prompt_id).template.format(question=question, context=context)

    def register(self, prompt: PromptTemplate) -> None:
        self.prompts[prompt.id] = prompt


def format_context(results: list[SearchResult]) -> str:
    blocks = []
    for index, result in enumerate(results, start=1):
        source = result.metadata.get("source_path") or result.metadata.get("filename") or result.id
        blocks.append(
            f"[S{index}] source={source} score={result.score:.4f}\n{result.text}"
        )
    return "\n\n".join(blocks)
