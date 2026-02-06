# python/app/sentiment.py
from transformers import pipeline
import logging
import torch

# Configuração de Log
logger = logging.getLogger("horaculo.sentiment")

_FINBERT_PIPELINE = None

def get_pipeline():
    """
    Singleton que carrega o FinBERT na GPU se disponível.
    """
    global _FINBERT_PIPELINE
    if _FINBERT_PIPELINE is None:
        # Detecção automática de GPU (CUDA)
        # device=0 seleciona a primeira GPU, -1 seleciona CPU
        device = 0 if torch.cuda.is_available() else -1
        
        # Nome do dispositivo para fins de log
        if device == 0:
            device_name = torch.cuda.get_device_name(0)
        else:
            device_name = "CPU"
        
        logger.info(f"Carregando modelo FinBERT em: {device_name}")
        
        _FINBERT_PIPELINE = pipeline(
            "sentiment-analysis", 
            model="ProsusAI/finbert",
            device=device  # 0 = GPU, -1 = CPU
        )
    return _FINBERT_PIPELINE

def batch_sentiment_score(texts):
    """
    Processa uma lista de textos de uma só vez (Batching).
    Extremamente mais rápido em GPU do que chamar um por um.
    """
    pipe = get_pipeline()
    results = []
    
    # Truncamos cada texto para 512 caracteres para evitar erro de limite do BERT.
    # O pipeline também suporta truncation=True, mas cortar a string antes economiza memória.
    truncated_texts = [str(t)[:512] for t in texts]
    
    try:
        # O pipeline do HF aceita listas diretamente
        # batch_size=16 é um bom ponto de partida; aumente se tiver muita VRAM (ex: 32 ou 64)
        predictions = pipe(truncated_texts, batch_size=16, truncation=True) 
        
        for res in predictions:
            label = res['label']
            score = res['score']
            
            if label == 'positive':
                results.append(score)      # 0.0 a 1.0
            elif label == 'negative':
                results.append(-score)     # -1.0 a 0.0
            else: # neutral
                results.append(0.0)
                
    except Exception as e:
        logger.error(f"Erro no Batch FinBERT: {e}")
        # Fallback: retorna zeros (neutro) se falhar, mantendo o tamanho da lista correto
        return [0.0] * len(texts)
        
    return results

# Mantemos a função singular apenas para compatibilidade ou testes unitários
def simple_sentiment_score(text: str) -> float:
    """
    Wrapper para processar um único texto usando a lógica de batch.
    """
    if not text:
        return 0.0
    return batch_sentiment_score([text])[0]
