# python/app/cache.py
import json
import redis
import os
import logging
import hashlib

logger = logging.getLogger("horaculo.cache")

# Conecta ao mesmo Redis do Celery
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.from_url(REDIS_URL)

def get_cache_key(prefix, **kwargs):
    """Gera uma chave única baseada nos argumentos (ex: query='oil')."""
    # Ordena as chaves para garantir consistência (a=1, b=2 é igual a b=2, a=1)
    s = json.dumps(kwargs, sort_keys=True)
    hash_str = hashlib.md5(s.encode('utf-8')).hexdigest()
    return f"horaculo:{prefix}:{hash_str}"

def check_cache(query_text: str):
    """Verifica se existe uma análise recente (TTL 10 min)."""
    key = get_cache_key("analysis", q=query_text.lower().strip())
    data = r.get(key)
    if data:
        logger.info(f"CACHE HIT para: {query_text}")
        return json.loads(data)
    return None

def set_cache(query_text: str, result: dict, ttl=600):
    """Salva o resultado no Redis por 10 minutos (600s)."""
    try:
        key = get_cache_key("analysis", q=query_text.lower().strip())
        r.setex(key, ttl, json.dumps(result))
    except Exception as e:
        logger.error(f"Falha ao salvar cache: {e}")
