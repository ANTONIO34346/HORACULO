# python/app/worker.py
from celery import Celery
import os
import asyncio
from app.orchestrator import run_query
from app.sentiment import get_pipeline # Garante que o modelo carrega aqui

# Configuração do Celery apontando para o Redis
celery = Celery(__name__)
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
celery.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Tarefa Pesada
@celery.task(name="analyze_market_task", bind=True)
def analyze_market_task(self, query, newsapi_key, use_openai, openai_key):
    """
    Esta função corre no container 'worker'.
    É aqui que o FinBERT e o C++ Core vão rodar, libertando a API.
    """
    # Nota: run_query é síncrona, perfeito para o Celery worker
    try:
        print(f"I [Worker] Iniciando análise para: {query}")
        
        # O modelo FinBERT será carregado na memória deste processo worker
        # e mantido vivo entre requisições (Singleton no processo)
        result = run_query(
            query=query, 
            newsapi_key=newsapi_key, 
            use_openai=use_openai, 
            openai_key=openai_key
        )
        return result
    except Exception as e:
        # Log de erro e re-raise para o Celery marcar como FAILED
        print(f"E [Worker] Falha: {e}")
        raise e
