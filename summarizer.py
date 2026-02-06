# python/app/summarizer.py
import os
import logging
import re

logger = logging.getLogger("horaculo.summarizer")

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


# ======================================================
# TOKEN SIEVE — LIMPEZA AGRESSIVA
# ======================================================
STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "in", "on", "at", "for",
    "to", "of", "with", "by", "from", "as", "is", "are", "was", "were",
    "be", "been", "this", "that", "these", "those", "it", "its",
    "will", "would", "could", "should", "may", "might", "can",
}

BOILERPLATE_PATTERNS = [
    r"copyright.*?reserved\.?",
    r"all rights reserved\.?",
    r"reuters",
    r"associated press",
    r"©\s?\d{4}",
]

def token_sieve(text: str) -> str:
    if not text:
        return ""

    # lowercase
    text = text.lower()

    # remove boilerplate jurídico/jornalístico
    for pattern in BOILERPLATE_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # remove pontuação inútil
    text = re.sub(r"[^\w\s\.\-]", "", text)

    # remove stopwords
    words = [
        w for w in text.split()
        if w not in STOPWORDS and len(w) > 2
    ]

    return " ".join(words)


# ======================================================
# FALLBACK LOCAL
# ======================================================
def local_summary(texts):
    if not texts:
        return "Sem dados para resumir."

    summary = "Resumo Local:\n"
    for t in texts[:3]:
        clean = token_sieve(t)
        summary += f"- {clean[:150]}...\n"
    return summary


# ======================================================
# OPENAI STRATEGIC ANALYSIS
# ======================================================
def openai_strategic_analysis(data_payload, api_key=None, model="gpt-4o-mini"):
    if not HAS_OPENAI:
        return "ERRO: Biblioteca 'openai' não instalada."

    final_api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not final_api_key:
        return "ERRO: API Key da OpenAI não fornecida."

    try:
        client = OpenAI(api_key=final_api_key)

        # ------------------------------
        # EXTRAÇÃO + LIMPEZA
        # ------------------------------
        raw_texts = data_payload.get("raw_texts", [])[:10]
        cleaned_texts = [token_sieve(t) for t in raw_texts]

        verdict_expl = data_payload.get("verdict", "N/A")
        intensity = data_payload.get("intensity", 0.0)
        eden_data = data_payload.get("eden_signal", {})
        eden_str = (
            f"DETECTADO ({eden_data.get('source')})"
            if eden_data.get("detected")
            else "NÃO DETECTADO"
        )
        psych = data_payload.get("psychology", {})
        hard_data = token_sieve(data_payload.get("hard_data", ""))
        memory = token_sieve(data_payload.get("memory_context", ""))
        clusters = token_sieve(data_payload.get("cluster_context", ""))

        # ------------------------------
        # PROMPT OTIMIZADO
        # ------------------------------
        prompt = f"""
ANALISTA MACRO SÊNIOR. IGNORE RUÍDO. EXTRAIA SINAL.

HORACULO:
veredito={verdict_expl}
intensidade={intensity:.3f}
eden={eden_str}
psicologia={psych.get('mood', 'neutro')} crowded={psych.get('is_crowded')}

DADOS:
{hard_data}

NARRATIVAS:
{clusters}

MEMÓRIA:
{memory}

NOTÍCIAS (LIMPAS):
{cleaned_texts}

TAREFA:
1 incentivos
2 dados vs manchete
3 assimetria
4 cenários base otimista pessimista
"""

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Senior investment strategist detecting market manipulation."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=1000
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Erro na OpenAI: {e}")
        return f"Falha na geração do resumo estratégico: {str(e)}"
