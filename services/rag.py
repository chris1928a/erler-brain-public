"""FAISS RAG search — downloads index from S3, searches locally."""
import os
import json
import tempfile
import logging
import numpy as np
import boto3

logger = logging.getLogger("rag")

BUCKET = os.environ.get("BRAIN_BUCKET", "")
s3 = boto3.client("s3", region_name="eu-central-1")

# Cache index in memory
_index = None
_chunks = None


def _load_index():
    """Download FAISS index and chunks from S3 (cached after first load)."""
    global _index, _chunks
    if _index is not None:
        return

    import faiss

    with tempfile.TemporaryDirectory() as tmpdir:
        # Download index
        idx_path = os.path.join(tmpdir, "faiss.index")
        s3.download_file(BUCKET, "faiss.index", idx_path)
        _index = faiss.read_index(idx_path)

        # Download chunks
        chunks_path = os.path.join(tmpdir, "chunks.json")
        s3.download_file(BUCKET, "chunks.json", chunks_path)
        with open(chunks_path) as f:
            _chunks = json.load(f)

    logger.info("FAISS index loaded: %d vectors, %d chunks", _index.ntotal, len(_chunks))


def _embed_query(text: str) -> np.ndarray:
    """Simple embedding using Gemini (or cached model)."""
    from google import genai
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    result = client.models.embed_content(
        model="models/text-embedding-004",
        contents=text,
    )
    return np.array(result.embeddings[0].values, dtype=np.float32).reshape(1, -1)


async def search(query: str, top_k: int = 5) -> list:
    """Search FAISS index for relevant chunks."""
    _load_index()

    query_vec = _embed_query(query)
    distances, indices = _index.search(query_vec, top_k)

    results = []
    for i, idx in enumerate(indices[0]):
        if idx < 0 or idx >= len(_chunks):
            continue
        chunk = _chunks[idx]
        results.append({
            "text": chunk.get("text", ""),
            "source": chunk.get("source", "unknown"),
            "score": float(distances[0][i]),
        })
    return results
