# python/app/alerts.py
import os
import requests
import logging

logger = logging.getLogger("horaculo.alerts")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

TELEGRAM_BOT = os.getenv("TG_BOT_TOKEN")
TELEGRAM_CHAT = os.getenv("TG_CHAT_ID")

def send_telegram(text, timeout=10):
    if not TELEGRAM_BOT or not TELEGRAM_CHAT:
        logger.debug("Telegram not configured; skipping send_telegram")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": TELEGRAM_CHAT, "text": text}, timeout=timeout)
        if not r.ok:
            logger.warning("Telegram send failed: status=%s body=%s", r.status_code, r.text[:500])
    except requests.RequestException as e:
        logger.exception("Error sending Telegram message: %s", e)