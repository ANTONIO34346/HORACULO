# python/app/api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from celery.result import AsyncResult
from app.worker import analyze_market_task, celery
from app.variants.crypto import CryptoSatellite # Importa o Satélite
import os
import logging

app = FastAPI()
logger = logging.getLogger("horaculo.api")

# Modelo de Input
class Query(BaseModel):
    q: str
    use_openai: bool = False

# --- ROTA 1: MERCADO TRADICIONAL (Async/Celery) ---
@app.post("/analyze/submit")
async def submit_analysis(q: Query):
    """
    Inicia o motor completo (Macro, Commodities) via Celery Worker.
    """
    task = analyze_market_task.delay(
        query=q.q,
        newsapi_key=os.getenv("NEWSAPI_KEY"),
        use_openai=q.use_openai,
        openai_key=os.getenv("OPENAI_API_KEY")
    )
    return {"task_id": task.id, "status": "processing"}

@app.get("/analyze/status/{task_id}")
async def get_status(task_id: str):
    """
    Polling para o Frontend Web/Mobile.
    """
    task_result = AsyncResult(task_id, app=celery)
    
    if task_result.state == 'SUCCESS':
        return {
            "state": "SUCCESS",
            "ui": task_result.result.get("ui"), # Payload formatado para as Telas 1-4
            "full_data": task_result.result
        }
    elif task_result.state == 'FAILURE':
        return {"state": "FAILURE", "error": str(task_result.info)}
    
    return {"state": task_result.state}

# --- ROTA 2: SATÉLITE CRIPTO (Sync/Fast) ---
@app.post("/analyze/crypto")
async def analyze_crypto(q: Query):
    """
    Rota direta para a 5ª Tela (Cripto).
    Ignora filas do Celery para resposta imediata.
    """
    try:
        logger.info(f"Iniciando Satélite Cripto para: {q.q}")
        satellite = CryptoSatellite()
        result = satellite.run_analysis(q.q)
        return result
    except Exception as e:
        logger.error(f"Erro no Satélite Cripto: {e}")
        raise HTTPException(status_code=500, detail=str(e))
