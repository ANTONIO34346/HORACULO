# python/app/psychology.py

def analyze_market_psychology(sentiments, verdict_intensity, coordination_score):
    """
    Mede a saúde psicológica da narrativa de mercado.
    Retorna sinais de euforia, medo, crowded trade e armadilhas narrativas.
    """

    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0

    # Crowded Trade: consenso forte + emoção extrema
    is_crowded = verdict_intensity > 0.7 and abs(avg_sentiment) > 0.6

    # Narrative Trap: coordenação artificial + emoção extrema
    is_trap = coordination_score > 0.5 and abs(avg_sentiment) > 0.7

    if avg_sentiment > 0.2:
        mood = "Euforia"
    elif avg_sentiment < -0.2:
        mood = "Medo"
    else:
        mood = "Neutro"

    psych_report = {
        "mood": mood,
        "sentiment_score": round(avg_sentiment, 3),
        "is_crowded": is_crowded,
        "is_trap": is_trap,
        # Assimetria ALTA = mercado interessante (ou perigoso, mas lucrável)
        "asymmetry_level": "ALTA" if (is_trap or not is_crowded) else "BAIXA"
    }

    return psych_report
