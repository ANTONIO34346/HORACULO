# python/app/anti_manipulation.py
from collections import Counter

def score_coordination(sources_list):
    # sources_list: list of source names
    c = Counter(sources_list)
    most_common = c.most_common(3)
    # if many entries from few sources -> coordination signal
    total = sum(c.values())
    top_sum = sum([x[1] for x in most_common])
    return top_sum/total if total>0 else 0.0
