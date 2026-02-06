import core
import datetime
import logging
import json
import numpy as np
from collections import defaultdict

# 🔹 INFRA
from app.cache import check_cache, set_cache
from app.ingest import fetch_data_entrypoint

# 🔹 INTELIGÊNCIA
from embeddings import embed_texts
from dedupe import dedupe_by_embeddings
from claim_extract import batch_extract_claims
from sentiment import batch_sentiment_score
from clustering import cluster_embeddings

# 🔹 MEMÓRIA
from memory import (
    init_db,
    get_profile,
    upsert_profile,
    get_similar_events,
    get_trusted_weight,
    store_event
)

# 🔹 ANÁLISE
from anti_manipulation import score_coordination
from psychology import analyze_market_psychology
from summarizer import local_summary, openai_strategic_analysis
from data_extractor import extract_hard_data, format_data_for_prompt
from alerts import send_telegram

logger = logging.getLogger("horaculo.orchestrator")
init_db()

# ==========================================================
# UTIL
# ==========================================================

def calculate_entropy(scores: list) -> float:
    if not scores or sum(scores) == 0:
        return 0.0
    arr = np.array(scores)
    probs = arr / arr.sum()
    return float(-np.sum(probs * np.log(probs + 1e-9)))


def score_source_credibility(source: str) -> float:
    trusted = get_trusted_weight(source)
    if trusted:
        return trusted

    profile = get_profile(source)
    if not profile:
        return 0.5

    hits = profile.get("consensus_hits", 0)
    total = profile.get("total_scans", 0)

    if total < 5:
        return (0.5 * 5 + hits) / (5 + total)

    return max(0.1, min(0.9, hits / total))


def update_memory(items, verdict, winner):
    for it in items:
        src = it["source"]
        profile = get_profile(src) or {"total_scans": 0, "consensus_hits": 0}
        profile["total_scans"] += 1

        sim = verdict.source_scores.get(src, 0.0)
        if src == winner or sim > 0.85:
            profile["consensus_hits"] += 1

        upsert_profile(src, profile)

# ==========================================================
# MAIN
# ==========================================================

def run_query(query, newsapi_key=None, use_openai=False, openai_key=None):
    start = datetime.datetime.now()
    logger.info(f"🚀 QUERY: {query}")

    cached = check_cache(query)
    if cached:
        return cached

    items = fetch_data_entrypoint(query, newsapi_key)
    if not items:
        return {"error": "NO_DATA"}

    texts = [i["text"] for i in items]
    claims = batch_extract_claims(texts)
    embeddings = embed_texts(claims)

    items_kept, embs_kept = dedupe_by_embeddings(items, embeddings, 0.92)
    if not items_kept:
        return {"error": "FILTERED"}

    kept_texts = [i["text"] for i in items_kept]
    kept_sources = [i["source"] for i in items_kept]

    sentiments = batch_sentiment_score(kept_texts)
    credibility = [score_source_credibility(s) for s in kept_sources]

    cluster_labels = cluster_embeddings(
        embs_kept,
        k=min(4, max(2, len(embs_kept) // 5))
    )

    engine = core.HoraculoEngine(0.92)
    verdicts = engine.analyze_batch(embs_kept, kept_sources)

    best_idx = 0
    best_score = -1
    global_entropy = 0.0

    for i, v in enumerate(verdicts):
        centrality = sum(v.source_scores.values())
        score = centrality * (1 + credibility[i])
        if score > best_score:
            best_score = score
            best_idx = i
            global_entropy = calculate_entropy(list(v.source_scores.values()))

    final_verdict = verdicts[best_idx]
    winner_source = kept_sources[best_idx]

    update_memory(items_kept, final_verdict, winner_source)

    coordination_score = score_coordination(kept_sources)
    psych_report = analyze_market_psychology(
        sentiments,
        final_verdict.intensity,
        coordination_score
    )

    trust = score_source_credibility(winner_source)
    eden_signal = {
        "detected": trust > 0.85 and final_verdict.intensity < 0.5,
        "source": winner_source if trust > 0.85 else None,
        "confidence": trust
    }

    hard_data = extract_hard_data(kept_texts)
    data_evidence = format_data_for_prompt(hard_data)

    clusters_map = defaultdict(list)
    for i, cid in enumerate(cluster_labels):
        clusters_map[cid].append(
            f"[{kept_sources[i]}] {kept_texts[i][:160]}"
        )

    cluster_context = "\n".join(
        f"Grupo {k}: {' | '.join(v[:2])}"
        for k, v in clusters_map.items()
    )

    analysis_payload = {
        "raw_texts": kept_texts,
        "verdict": final_verdict.explanation,
        "intensity": final_verdict.intensity,
        "psychology": psych_report,
        "hard_data": data_evidence,
        "cluster_context": cluster_context,
        "eden_signal": eden_signal,
        "entropy": global_entropy
    }

    summary = (
        openai_strategic_analysis(analysis_payload, openai_key)
        if use_openai else
        local_summary(kept_texts)
    )

    # ==========================================================
    # UI PAYLOAD (🔥 O QUE PEDISTE)
    # ==========================================================

    ui_payload = {

        # TELA 1 — RADAR
        "screen_arbitrage": {
            "points": [
                {
                    "source": items_kept[i]["source"],
                    "sentiment": sentiments[i],
                    "credibility": get_trusted_weight(items_kept[i]["source"]) or 0.5,
                    "label": items_kept[i]["title"][:50]
                }
                for i in range(len(items_kept))
            ],
            "eden_detected": eden_signal["detected"],
            "eden_source": eden_signal["source"],
            "intensity_score": float(final_verdict.intensity)
        },

        # TELA 2 — INTELIGÊNCIA
        "screen_intelligence": {
            "clusters": [
                {
                    "id": cid,
                    "sources": [
                        items_kept[i]["source"]
                        for i, c in enumerate(cluster_labels) if c == cid
                    ],
                    "sentiment_avg": float(np.mean([
                        sentiments[i]
                        for i, c in enumerate(cluster_labels) if c == cid
                    ]))
                }
                for cid in set(cluster_labels)
            ],
            "coordination_score": coordination_score
        },

        # TELA 3 — PSICOLOGIA
        "screen_stress": {
            "entropy": float(global_entropy),
            "mood": psych_report["mood"],
            "is_trap": psych_report["is_trap"],
            "is_crowded": psych_report["is_crowded"],
            "asymmetry": psych_report["asymmetry_level"]
        },

        # TELA 4 — PORTAL
        "screen_portal": {
            "summary": summary,
            "hard_data": hard_data,
            "meta": {
                "execution_time": f"{(datetime.datetime.now()-start).total_seconds():.2f}s",
                "sources_count": len(items_kept)
            }
        }
    }

    # ==========================================================
    # RESULT FINAL
    # ==========================================================

    result_json = {
        "verdict": {
            "winner_source": winner_source,
            "intensity": float(final_verdict.intensity),
            "entropy": float(global_entropy),
            "inconclusive": global_entropy > 1.8
        },
        "eden_signal": eden_signal,
        "psychology": psych_report,
        "summary": summary,
        "hard_data": hard_data,
        "ui": ui_payload,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

    set_cache(query, result_json)

    if eden_signal["detected"] or final_verdict.intensity > 0.6:
        send_telegram(f"🚨 EDEN SIGNAL\n{query}\n{summary[:200]}")

    return result_json
