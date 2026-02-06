# python/app/embeddings.py

import hashlib
import json
import redis
from sentence_transformers import SentenceTransformer

# ----------------------------
# CONFIG REDIS
# ----------------------------
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_TTL = 60 * 60 * 24 * 7  # 7 dias

_rds = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

# ----------------------------
# MODEL SINGLETON
# ----------------------------
_MODEL = None

def load_model(name="all-mpnet-base-v2"):
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(name)
    return _MODEL

# ----------------------------
# EMBEDDING COM CACHE
# ----------------------------
def get_embedding(text: str):
    """
    Retorna embedding com cache Redis.
    """
    text = text.strip()
    text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
    key = f"emb:{text_hash}"

    # 1️⃣ Cache
    cached = _rds.get(key)
    if cached:
        return json.loads(cached)

    # 2️⃣ GPU (caro)
    model = load_model()
    emb = model.encode(
        text,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    emb_list = emb.tolist()

    # 3️⃣ Salva no Redis
    _rds.setex(key, REDIS_TTL, json.dumps(emb_list))

    return emb_list


def embed_texts(texts):
    """
    Versão em lote usando cache individual.
    """
    return [get_embedding(t) for t in texts]
