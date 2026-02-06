# python/app/clustering.py
from sklearn.cluster import KMeans
import numpy as np

def cluster_embeddings(embs, k=3):
    if len(embs) < k+1:
        return [0]*len(embs)
    X = np.array(embs)
    km = KMeans(n_clusters=k, random_state=42).fit(X)
    return km.labels_.tolist()
