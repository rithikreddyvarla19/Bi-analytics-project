# Architecture

```mermaid
flowchart LR
    subgraph Sources
        PDF[PDF Files]
        CSV[CSV Files]
        TXT[Text Files]
    end

    subgraph Ingestion
        Loader[Document Loaders]
        Chunker[Recursive Chunker]
        Embed[Embedding Pipeline]
    end

    subgraph Retrieval
        FAISS[FAISS Vector Index]
        Retriever[Retriever]
    end

    subgraph Generation
        Prompt[Prompt Registry]
        LLM[OpenAI or HuggingFace LLM]
        API[FastAPI Chat API]
    end

    subgraph Evaluation
        GT[Ground Truth Dataset]
        Metrics[Faithfulness, Hallucination Rate, Context Precision, Context Recall, Answer Relevancy]
        MLflow[MLflow Tracking]
    end

    subgraph Monitoring
        Postgres[(PostgreSQL)]
        Feedback[User Feedback]
        Streamlit[Streamlit Dashboard]
    end

    PDF --> Loader
    CSV --> Loader
    TXT --> Loader
    Loader --> Chunker --> Embed --> FAISS
    FAISS --> Retriever --> Prompt --> LLM --> API
    API --> Feedback --> Postgres
    API --> Metrics
    GT --> Metrics --> MLflow
    MLflow --> Streamlit
    Postgres --> Streamlit
```

## Data Flow

1. Source documents are loaded from PDFs, CSVs, and text files.
2. Documents are normalized, checksummed, and split into overlapping chunks.
3. Embeddings are generated with OpenAI, HuggingFace Transformers, or deterministic hashing for local runs.
4. Chunks and vectors are written to a FAISS index.
5. FastAPI retrieves top-k chunks, renders a governed prompt, calls the selected LLM, and returns source-cited answers.
6. Evaluation jobs compare generated answers against validated ground truth and log metrics to MLflow.
7. Streamlit displays quality metrics, hallucination trends, latency, feedback, and prompt comparisons.
