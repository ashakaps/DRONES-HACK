import os, asyncio, logging
from typing import Optional, Tuple, Dict, Any
import asyncpg

log = logging.getLogger("db")

_pool: Optional[asyncpg.Pool] = None
_dsn = os.getenv("DB_DSN", "postgresql://postgres:postgres@db:5432/droneradar")

CREATE_SQL = '''
CREATE TABLE IF NOT EXISTS drone_points(
  drone_id TEXT,
  ts TIMESTAMPTZ NOT NULL,
  lat DOUBLE PRECISION NOT NULL,
  lon DOUBLE PRECISION NOT NULL,
  alt DOUBLE PRECISION,
  speed DOUBLE PRECISION
);
'''

async def ensure_pool(retries: int = 20, delay: float = 1.0) -> Optional[asyncpg.Pool]:
    """Создаёт пул соединений с ретраями. Не падает, если DB_STRICT=0."""
    global _pool
    if _pool:
        return _pool
    last_exc = None
    for i in range(retries):
        try:
            _pool = await asyncpg.create_pool(_dsn, min_size=1, max_size=5)
            log.info("DB pool created")
            return _pool
        except Exception as e:
            last_exc = e
            log.warning("DB connect try %s/%s failed: %s", i+1, retries, e)
            await asyncio.sleep(delay)
    log.error("DB connection failed after retries: %s", last_exc)
    return None

async def init_db() -> None:
    pool = await ensure_pool()
    if not pool:
        log.warning("init_db skipped (no pool)")
        return
    async with pool.acquire() as conn:
        await conn.execute(CREATE_SQL)
    log.info("DB schema ensured")

async def ping() -> Tuple[bool, Dict[str, Any]]:
    pool = await ensure_pool()
    if not pool:
        return False, {"reason": "no_pool"}
    try:
        async with pool.acquire() as conn:
            v = await conn.fetchval("SELECT 1")
            return v == 1, {"value": v}
    except Exception as e:
        return False, {"error": str(e)}

async def status() -> Dict[str, Any]:
    pool = await ensure_pool()
    return {
        "dsn": _dsn,
        "pool_ready": bool(pool),
    }
