# python/app/claim_extract.py
import re
from typing import List

def extract_claim(text: str) -> str:
    # heuristics: take first sentence or clause with verbs like "will", "to", "says", "announces"
    s = text.strip()
    if not s: return ""
    # split by punctuation
    parts = re.split(r'\.|\!|\?', s)
    if parts:
        first = parts[0].strip()
        if len(first.split()) < 6 and len(parts) > 1:
            # try second
            return parts[1].strip()[:300]
        return first[:300]
    return s[:300]

def batch_extract_claims(texts: List[str]):
    return [extract_claim(t) for t in texts]
