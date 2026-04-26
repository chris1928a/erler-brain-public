#!/usr/bin/env python3
"""
Build a FAISS index over your local markdown / text docs for the Brain's /brain command.

Usage:
    python scripts/build_rag_index.py /path/to/docs

Walks the directory, chunks each markdown file by heading, embeds chunks via Gemini,
and writes a FAISS index + chunks pickle to .chunks/ at the project root.

The Brain (services/rag.py) loads these on startup. Re-run this script whenever your
source docs change.
"""
import os
import pickle
import re
import sys
from pathlib import Path

try:
    import faiss
    import numpy as np
    from google import genai
except ImportError:
    sys.exit("pip install -r requirements.txt")

if len(sys.argv) < 2:
    sys.exit("Usage: python scripts/build_rag_index.py /path/to/docs")

DOCS_DIR = Path(sys.argv[1]).resolve()
if not DOCS_DIR.is_dir():
    sys.exit(f"Not a directory: {DOCS_DIR}")

OUT_DIR = Path(__file__).parent.parent / ".chunks"
OUT_DIR.mkdir(exist_ok=True)

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_KEY:
    sys.exit("Set GEMINI_API_KEY env var first")

client = genai.Client(api_key=GEMINI_KEY)


def chunk_markdown(text: str, source: str) -> list[dict]:
    """Split markdown by H2 headings into chunks with source metadata."""
    chunks = []
    blocks = re.split(r"\n(?=## )", text)
    for block in blocks:
        block = block.strip()
        if len(block) < 100:
            continue
        chunks.append({"text": block[:3000], "source": source})
    return chunks


print(f"Walking {DOCS_DIR}...")
all_chunks: list[dict] = []
for path in DOCS_DIR.rglob("*.md"):
    rel = path.relative_to(DOCS_DIR)
    text = path.read_text(encoding="utf-8", errors="ignore")
    all_chunks.extend(chunk_markdown(text, str(rel)))

print(f"Got {len(all_chunks)} chunks. Embedding via Gemini...")

embeddings: list[list[float]] = []
for i, chunk in enumerate(all_chunks):
    if i % 50 == 0:
        print(f"  {i}/{len(all_chunks)}")
    resp = client.models.embed_content(
        model="text-embedding-004",
        contents=chunk["text"],
    )
    embeddings.append(resp.embeddings[0].values)

vectors = np.array(embeddings, dtype="float32")
index = faiss.IndexFlatL2(vectors.shape[1])
index.add(vectors)

faiss.write_index(index, str(OUT_DIR / "index.faiss"))
with (OUT_DIR / "chunks.pkl").open("wb") as f:
    pickle.dump(all_chunks, f)

print(f"\nDone. Index has {index.ntotal} vectors. Output: {OUT_DIR}/")
