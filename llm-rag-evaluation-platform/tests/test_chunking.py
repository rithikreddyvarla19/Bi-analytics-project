from ingestion.chunking import RecursiveTextChunker
from ingestion.loaders import RawDocument


def test_chunker_creates_overlapping_chunks() -> None:
    document = RawDocument(
        id="doc-1",
        text="Alpha beta gamma. " * 80,
        source_path="sample.txt",
        source_type="txt",
        checksum="abc",
    )
    chunker = RecursiveTextChunker(chunk_size=120, chunk_overlap=20)

    chunks = chunker.chunk_document(document)

    assert len(chunks) > 1
    assert chunks[0].document_id == "doc-1"
    assert all(chunk.token_count > 0 for chunk in chunks)
    assert chunks[1].metadata["chunk_index"] == 1
