# python/app/variants/crypto.py
import feedparser
import asyncio
import httpx
import logging
from typing import List, Dict

# Importações do Core do Horaculo
import core  # O motor C++
from app.embeddings import get_embedding #
from app.sentiment import batch_sentiment_score #
from app.data_extractor import extract_hard_data #

logger = logging.getLogger("horaculo.crypto")

class CryptoSatellite:
    def __init__(self):
        # Threshold ajustado para 0.82 para capturar gírias de cripto
        # O Motor C++ é instanciado aqui de forma isolada
        self.engine = core.HoraculoEngine(copy_threshold=0.82)
        
        # Fontes de Elite (RSS Público)
        self.feeds = [
            "https://cointelegraph.com/rss",
            "https://cryptoslate.com/feed/",
            "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "https://en.bitcoinsistemi.com/feed/",
            "https://beincrypto.com/feed/"
        ]

    async def _fetch_rss(self, asset: str) -> List[Dict]:
        """Busca assíncrona de sinais em feeds RSS."""
        signals = []
        async with httpx.AsyncClient() as client:
            for url in self.feeds:
                try:
                    resp = await client.get(url, timeout=8.0)
                    feed = feedparser.parse(resp.text)
                    for entry in feed.entries[:10]: # Top 10 mais recentes
                        # Filtro insensível a maiúsculas
                        if asset.lower() in entry.title.lower() or asset.lower() in entry.summary.lower():
                            signals.append({
                                "source": feed.feed.title if hasattr(feed.feed, 'title') else "Crypto Source",
                                "text": f"{entry.title}. {entry.summary[:300]}",
                                "url": entry.link,
                                "published": entry.get("published", "")
                            })
                except Exception as e:
                    logger.warning(f"Falha ao ler feed {url}: {e}")
        return signals

    def _get_action_signal(self, conflict: float, sentiment: float, is_panic: bool) -> Dict:
        """
        Lógica de Assimilação Rápida (Aggressive UI).
        Traduz números em Cores e Ícones.
        """
        # 1. PÂNICO (Caveira)
        if is_panic:
            return {"code": "ABORT / CRASH", "color": "#FF0000", "icon": "skull"}
        
        # 2. ARMADILHA (Olho) - Alta coordenação (conflito alto) + Sentimento Positivo Artificial
        if conflict > 0.70 and sentiment > 0.4:
            return {"code": "TRAP / FAKE PUMP", "color": "#FACC15", "icon": "eye"} # Yellow-400
        
        # 3. BULLISH (Foguete) - Baixo conflito (consenso orgânico) + Sentimento Positivo
        if conflict < 0.4 and sentiment > 0.3:
            return {"code": "STRONG BUY", "color": "#22C55E", "icon": "rocket"} # Green-500
        
        # 4. INCERTO (Escudo) - Conflito moderado ou Sentimento Neutro
        return {"code": "HODL / WAIT", "color": "#A855F7", "icon": "shield"} # Purple-500

    def run_analysis(self, asset: str):
        # 1. Busca de Sinais
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        raw_signals = loop.run_until_complete(self._fetch_rss(asset))

        if not raw_signals:
            return {
                "status": "no_data", 
                "asset": asset,
                "action_signal": {"code": "NO SIGNAL", "color": "#64748B", "icon": "cloud-off"}
            }

        # 2. Processamento Vetorial
        texts = [s['text'] for s in raw_signals]
        embeddings = [get_embedding(t) for t in texts]
        sentiments = batch_sentiment_score(texts)

        # 3. Arbitragem C++ (Core Engine)
        # Compara narrativa contra narrativa para ver quem está mentindo
        verdicts = self.engine.analyze_batch(embeddings, embeddings, [s['source'] for s in raw_signals])
        
        # 4. Cálculo de Métricas
        max_conflict = max([v.intensity for v in verdicts]) if verdicts else 0.0
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
        
        # Heurística de Pânico: Sentimento muito negativo + Alta confusão (conflito)
        is_panic = avg_sentiment < -0.35 and max_conflict > 0.65

        # 5. Output Visual (Semáforo)
        action = self._get_action_signal(max_conflict, avg_sentiment, is_panic)
        hard_data = extract_hard_data(texts)

        return {
            "status": "success",
            "asset": asset.upper(),
            "metrics": {
                "conflict_intensity": float(max_conflict),
                "sentiment_gap": float(avg_sentiment),
                "is_panic": is_panic
            },
            "action_signal": action, # O Frontend consome ISTO para pintar a tela
            "hard_data": hard_data,
            "signals": raw_signals[:8] # Retorna as 8 notícias mais relevantes
        }
