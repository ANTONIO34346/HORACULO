# python/app/dedupe.py
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def dedupe_by_embeddings(items, embeddings, threshold=0.92):
    keep = []
    keep_emb = []
    for i, emb in enumerate(embeddings):
        if not keep_emb:
            keep.append(items[i]); keep_emb.append(emb)
            continue
        sims = cosine_similarity([emb], keep_emb)[0]
        if sims.max() < threshold:
            keep.append(items[i]); keep_emb.append(emb)
    return keep, keep_emb
