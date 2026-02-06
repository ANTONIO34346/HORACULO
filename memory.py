# python/app/memory.py
import os
import json
import time
import logging
import sqlite3
import psycopg2

logger = logging.getLogger("horaculo.memory")

# URL do banco (definida no docker-compose ou env)
DATABASE_URL = os.getenv("DATABASE_URL")

# =========================
# CONEXÃO
# =========================

def get_db_connection():
    """
    Fábrica de conexões.
    - Postgres se DATABASE_URL existir
    - SQLite local como fallback (dev / standalone)
    """
    if DATABASE_URL:
        try:
            return psycopg2.connect(DATABASE_URL)
        except Exception as e:
            logger.error(f"Erro ao conectar no Postgres: {e}")
            raise
    else:
        conn = sqlite3.connect("memory.db")
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn


# =========================
# INIT DB
# =========================

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    if DATABASE_URL:
        # ---------- POSTGRES ----------
        cur.execute("""
            CREATE TABLE IF NOT EXISTS source_profile (
                source TEXT PRIMARY KEY,
                data TEXT,
                updated_at BIGINT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS event_history (
                id SERIAL PRIMARY KEY,
                query TEXT,
                hard_data TEXT,
                verdict_summary TEXT,
                timestamp BIGINT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS trusted_sources (
                source TEXT PRIMARY KEY,
                weight REAL
            )
        """)
    else:
        # ---------- SQLITE ----------
        cur.execute("""
            CREATE TABLE IF NOT EXISTS source_profile (
                source TEXT PRIMARY KEY,
                data TEXT,
                updated_at INTEGER
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS event_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                hard_data TEXT,
                verdict_summary TEXT,
                timestamp INTEGER
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS trusted_sources (
                source TEXT PRIMARY KEY,
                weight REAL
            )
        """)

    # ---------- SEED ----------
    placeholder = "%s" if DATABASE_URL else "?"
    cur.execute("SELECT COUNT(*) FROM trusted_sources")
    count = cur.fetchone()[0]

    if count == 0:
        initial_sources = [
            ("reuters", 0.95),
            ("bloomberg", 0.95),
            ("ft", 0.95),
            ("financial times", 0.95),
            ("wsj", 0.95),
            ("wall street journal", 0.95),
        ]
        cur.executemany(
            f"INSERT INTO trusted_sources VALUES ({placeholder}, {placeholder})",
            initial_sources
        )
        logger.info("Seed inicial de fontes confiáveis aplicado.")

    conn.commit()
    conn.close()
    logger.info(f"Database inicializado ({'Postgres' if DATABASE_URL else 'SQLite'}).")


# =========================
# PERFIL DE FONTE
# =========================

def upsert_profile(source: str, data: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    now = int(time.time())
    payload = json.dumps(data)

    if DATABASE_URL:
        cur.execute("""
            INSERT INTO source_profile (source, data, updated_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (source)
            DO UPDATE SET
                data = EXCLUDED.data,
                updated_at = EXCLUDED.updated_at
        """, (source, payload, now))
    else:
        cur.execute("""
            REPLACE INTO source_profile (source, data, updated_at)
            VALUES (?, ?, ?)
        """, (source, payload, now))

    conn.commit()
    conn.close()


def get_profile(source: str):
    conn = get_db_connection()
    cur = conn.cursor()
    placeholder = "%s" if DATABASE_URL else "?"
    cur.execute(f"SELECT data FROM source_profile WHERE source={placeholder}", (source,))
    row = cur.fetchone()
    conn.close()
    return json.loads(row[0]) if row else None


# =========================
# HISTÓRICO DE EVENTOS
# =========================

def store_event(query: str, hard_data: dict, verdict_summary: str):
    conn = get_db_connection()
    cur = conn.cursor()
    now = int(time.time())
    payload = json.dumps(hard_data)

    if DATABASE_URL:
        cur.execute("""
            INSERT INTO event_history (query, hard_data, verdict_summary, timestamp)
            VALUES (%s, %s, %s, %s)
        """, (query, payload, verdict_summary, now))
    else:
        cur.execute("""
            INSERT INTO event_history (query, hard_data, verdict_summary, timestamp)
            VALUES (?, ?, ?, ?)
        """, (query, payload, verdict_summary, now))

    conn.commit()
    conn.close()


def get_similar_events(query: str, limit: int = 2):
    conn = get_db_connection()
    cur = conn.cursor()

    if DATABASE_URL:
        cur.execute("""
            SELECT query, hard_data, verdict_summary
            FROM event_history
            WHERE query ILIKE %s
            ORDER BY timestamp DESC
            LIMIT %s
        """, (f"%{query}%", limit))
    else:
        cur.execute("""
            SELECT query, hard_data, verdict_summary
            FROM event_history
            WHERE query LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (f"%{query}%", limit))

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "query": r[0],
            "data": json.loads(r[1]),
            "verdict": r[2]
        }
        for r in rows
    ]


# =========================
# FONTES CONFIÁVEIS (TIER 1)
# =========================

def get_trusted_weight(source_name: str):
    conn = get_db_connection()
    cur = conn.cursor()
    s = source_name.lower()

    if DATABASE_URL:
        cur.execute("""
            SELECT weight
            FROM trusted_sources
            WHERE %s LIKE '%%' || source || '%%'
        """, (s,))
    else:
        cur.execute("""
            SELECT weight
            FROM trusted_sources
            WHERE ? LIKE '%' || source || '%'
        """, (s,))

    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def add_trusted_source(source: str, weight: float = 0.95):
    conn = get_db_connection()
    cur = conn.cursor()
    placeholder = "%s" if DATABASE_URL else "?"

    cur.execute(
        f"REPLACE INTO trusted_sources (source, weight) VALUES ({placeholder}, {placeholder})",
        (source.lower(), weight)
    )

    conn.commit()
    conn.close()
    logger.info(f"Fonte confiável adicionada: {source} ({weight})")
