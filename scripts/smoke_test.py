"""M0 smoke test: one embedding call, vision calls on one figure, and a Pinecone documents index.

Usage: uv run python scripts/smoke_test.py
Each stage prints OK or FAIL with a short reason. Key values are masked in all output.
The Pinecone stage creates a temporary index, uses it, and deletes it (only if this run made it).
"""

import base64
import os
import time

from app.config import PROJECT_ROOT, load_env

load_env()
SECRETS = [os.environ.get("OPENAI_API_KEY", ""), os.environ.get("PINECONE_API_KEY", "")]
EMBED_MODEL = "text-embedding-3-small"
VISION_MODELS = ["gpt-6.1-terra", "gpt-6.1-sol", "gpt-4o"]
FIGURE = PROJECT_ROOT / "backend/storage/assets/paper-003/v1/figure-1-p2.png"
TEST_INDEX = "researchiq-smoke-test"
NAMESPACE = "smoke"
DOCS = [
    ("d1", "Zeroth-order optimization fine-tunes language models using only forward passes."),
    ("d2", "KV cache compression stores keys and values with fewer bits for long contexts."),
    ("d3", "Federated fine-tuning shares sparse updates between clients to save memory."),
]


def mask(text: str) -> str:
    """Hide any secret value that might appear inside an error message."""
    for secret in filter(None, SECRETS):
        text = text.replace(secret, "<key>")
    return text


def report(stage: str, ok: bool, detail: str) -> None:
    """Print one result line."""
    print(f"[{'OK' if ok else 'FAIL'}] {stage}: {mask(detail)[:300]}")


def embed(texts: list[str]) -> list[list[float]]:
    """Embed texts with the OpenAI embedding model."""
    from openai import OpenAI

    response = OpenAI().embeddings.create(model=EMBED_MODEL, input=texts)
    return [item.embedding for item in response.data]


def check_embedding() -> None:
    """Stage 1: one embedding call."""
    try:
        vectors = embed([text for _, text in DOCS])
        report(
            "embedding", True, f"{EMBED_MODEL} returned {len(vectors)} vectors of {len(vectors[0])}"
        )
    except Exception as error:
        report("embedding", False, f"{type(error).__name__}: {error}")


def check_vision(model: str) -> None:
    """Stage 2: ask one model to describe the paper-003 Figure 1 crop."""
    from openai import OpenAI

    image = base64.b64encode(FIGURE.read_bytes()).decode()
    content = [
        {
            "type": "text",
            "text": "In one sentence: what does the left bar chart in this figure show?",
        },
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image}"}},
    ]
    start = time.time()
    try:
        reply = OpenAI().chat.completions.create(
            model=model, messages=[{"role": "user", "content": content}], max_completion_tokens=400
        )
        text = (reply.choices[0].message.content or "").strip().replace("\n", " ")
        report(f"vision {model}", bool(text), f"{time.time() - start:.1f}s | {text[:200]}")
    except Exception as error:
        report(f"vision {model}", False, f"{type(error).__name__}: {error}")


def make_index(pc) -> None:
    """Create the temporary schema index: one dense vector field and one BM25 text field."""
    from pinecone import SchemaBuilder

    schema = (
        SchemaBuilder()
        .add_dense_vector_field("embedding", dimension=1536, metric="cosine")
        .add_string_field("body", full_text_search={"language": "en"})
        .build()
    )
    pc.indexes.create(name=TEST_INDEX, schema=schema, timeout=300)


def search_index(index, vectors: list[list[float]]) -> None:
    """Upsert three documents, then run a dense search and a BM25 search with a filter."""
    from pinecone.models.documents.score_by import DenseVectorQuery, TextQuery

    documents = [
        {"_id": doc_id, "embedding": vec, "body": text, "docver": "paper-x:v1"}
        for (doc_id, text), vec in zip(DOCS, vectors, strict=True)
    ]
    index.documents.upsert(namespace=NAMESPACE, documents=documents)
    time.sleep(10)  # indexing is eventually consistent
    dense = index.documents.search(
        namespace=NAMESPACE,
        top_k=3,
        include_fields=["body"],
        score_by=[
            DenseVectorQuery(
                values=embed(["fine-tuning with forward passes only"])[0], field="embedding"
            )
        ],
    )
    report(
        "pinecone dense search",
        True,
        f"top hit {dense.matches[0]._id if hasattr(dense.matches[0], '_id') else dense.matches[0]}",
    )
    text = index.documents.search(
        namespace=NAMESPACE,
        top_k=3,
        include_fields=["body"],
        score_by=[TextQuery(query="federated", field="body")],
        filter={"docver": {"$eq": "paper-x:v1"}},
    )
    report("pinecone BM25 search + metadata filter", True, f"top hit {text.matches[0]}")


def check_pinecone() -> None:
    """Stage 3: create a temporary schema index, search it both ways, then delete it."""
    from pinecone import Pinecone

    pc = Pinecone()
    existed = pc.has_index(TEST_INDEX)
    created = False
    try:
        if not existed:
            make_index(pc)
            created = True
            report("pinecone create schema index", True, "dense vector + BM25 text field")
        index = pc.index(TEST_INDEX)
        search_index(index, embed([text for _, text in DOCS]))
    except Exception as error:
        report("pinecone", False, f"{type(error).__name__}: {error}")
    finally:
        if created:
            pc.indexes.delete(TEST_INDEX)
            report("pinecone cleanup", True, f"deleted {TEST_INDEX}")


def main() -> None:
    """Run the three stages in order."""
    check_embedding()
    for model in VISION_MODELS:
        check_vision(model)
    check_pinecone()


if __name__ == "__main__":
    main()
