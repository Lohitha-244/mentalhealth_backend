import os
import pickle
import numpy as np
import faiss
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "rag.index")
META_PATH = os.path.join(BASE_DIR, "rag_meta.pkl")

_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        print("Loading SentenceTransformer model...")
        _embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _embedder


def build_index(chunks: list[dict]):
    """
    chunks = [{"source": "...", "title": "...", "content": "..."}]
    """
    texts = [c["content"] for c in chunks]

    vectors = get_embedder().encode(texts, normalize_embeddings=True)
    vectors = np.array(vectors, dtype="float32")

    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine similarity because vectors are normalized
    index.add(vectors)

    faiss.write_index(index, INDEX_PATH)

    with open(META_PATH, "wb") as f:
        pickle.dump(chunks, f)


def retrieve_context(query: str, k: int = 4) -> str:
    """
    Returns top-k chunks as a single context string.
    """
    if not (os.path.exists(INDEX_PATH) and os.path.exists(META_PATH)):
        return ""  # RAG not built yet

    index = faiss.read_index(INDEX_PATH)

    with open(META_PATH, "rb") as f:
        chunks = pickle.load(f)

    q_vec = get_embedder().encode([query], normalize_embeddings=True)
    q_vec = np.array(q_vec, dtype="float32")

    scores, ids = index.search(q_vec, k)

    picked = []
    for idx in ids[0]:
        if idx == -1:
            continue
        c = chunks[idx]
        picked.append(
            f"[Source: {c.get('source', '')} | {c.get('title', '')}]\n{c.get('content', '')}"
        )

    return "\n\n---\n\n".join(picked)